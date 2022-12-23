import functools
import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Optional, Set

CORRECT_THREAD_ATTR = "correct_thread"


class Runner(object):
    def __init__(self, name=None):
        def init_thread():
            nonlocal self
            setattr(self._thread_local, CORRECT_THREAD_ATTR, True)
            logging.debug(f"init_thread(): Starting thread {self.name}")

        self.name: str = name
        self._guards: Set[object] = set()
        self._timers: Set[threading.Timer] = set()
        self._cancel_timers = False
        self._thread_local = threading.local()
        self._executor = ThreadPoolExecutor(1,
                                            thread_name_prefix=name,
                                            initializer=init_thread)

    def is_valid_thread(self):
        return getattr(self._thread_local, CORRECT_THREAD_ATTR, False)

    def run_on_executor(self, func, *args,
                        timeout: Optional[float] = None,
                        force_schedule: bool = False, **kwargs):
        if timeout is not None and timeout > 0:
            # We need to wrap future that is going
            # to be created after specified time passes
            future: Future = Future()
            timer = threading.Timer(timeout, lambda: ())

            @functools.wraps(func)
            def wrapper():
                nonlocal self, timer, future, func, args, kwargs

                self._timers.remove(timer)
                if self._cancel_timers:
                    return

                try:
                    executor_future = self._executor.submit(
                        func, *args, *kwargs)
                except Exception as exception:
                    future.set_exception(exception)
                    return

                def done_cb(fut: Future):
                    nonlocal future, executor_future
                    assert not fut.running() and fut == executor_future

                    future.set_result(executor_future.result())
                    exc = executor_future.exception()
                    if exc:
                        future.set_exception(exc)

                executor_future.add_done_callback(done_cb)

            self._timers.add(timer)
            timer.function = wrapper
            timer.daemon = True
            timer.start()
            return future

        if not self.is_valid_thread() or timeout is not None or force_schedule:
            return self._executor.submit(func, *args, *kwargs)

        # Run on this thread
        future = Future()
        try:
            future.set_result(func(*args, *kwargs))
        except BaseException as exception:
            future.set_exception(exception)

        return future

    def run_guarded(self, func, *args,
                    timeout=None, force_schedule=True, **kwargs):
        if self.is_guarded_pending(func):
            return

        self._guards.add(func)

        @functools.wraps(func)
        def wrapper():
            nonlocal self, func, args, kwargs

            self._guards.remove(func)
            func(*args, *kwargs)

        return self.run_on_executor(wrapper,
                                    timeout=timeout,
                                    force_schedule=force_schedule)

    def is_guarded_pending(self, func):
        return func in self._guards

    def __del__(self):
        logging.debug("__del__():")
        self._cancel_timers = True
        for timer in self._timers:
            timer.cancel()
            timer.join()

        self._executor.shutdown()


class Tasker(object):
    def __init__(self,
                 runner: Optional[Runner] = None,
                 parent: Optional["Tasker"] = None):
        assert not (runner is not None and parent is not None)
        if runner is not None:
            self._runner = runner
        elif parent is not None:
            assert parent.runner is not None
            self._runner = parent.runner
        else:
            self._runner = Runner(name=str(self))

    def is_tasker_thread(self):
        return self._runner.is_valid_thread()

    @property
    def runner(self) -> Runner:
        return self._runner

    def is_guarded_pending(self, func):
        return self._runner.is_guarded_pending(func)

    @staticmethod
    def handler(guarded=False, force_schedule=False):
        force_schedule_parent = force_schedule

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, timeout=None, force_schedule=False, **kwargs):
                self: Tasker = args[0]
                force_schedule = force_schedule or force_schedule_parent

                if guarded:
                    return self._runner.run_guarded(
                        func,
                        *args,
                        timeout=timeout,
                        force_schedule=force_schedule,
                        **kwargs,
                    )
                else:
                    return self._runner.run_on_executor(
                        func,
                        *args,
                        timeout=timeout,
                        force_schedule=force_schedule,
                        **kwargs,
                    )

            return wrapper

        return decorator

    @staticmethod
    def assert_executor(hard=False):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self: Tasker = args[0]
                if not self.is_tasker_thread():
                    logging.warning(
                        f"{func} was called on invalid non-task-runner thread")
                    assert self.is_tasker_thread()
                    if hard:
                        raise SystemError

                return func(*args, **kwargs)

            return wrapper

        return decorator
