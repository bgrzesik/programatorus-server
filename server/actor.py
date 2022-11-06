import functools
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Set

CORRECT_THREAD_ATTR = "correct_thread"


class Actor(object):
    def __init__(self, parent: "Actor" = None, executor: ThreadPoolExecutor = None):
        def init_actor_thread(self: Actor):
            setattr(self._thread_local, CORRECT_THREAD_ATTR, True)
            logging.debug(f"init_actor_thread(): Starting thread for {self.__class__.__name__} {self}")

        self._guards = set()
        self._timers: Set[threading.Timer] = set()
        self._cancel_timers = False
        self._thread_local = threading.local()

        if parent is not None:
            assert executor is None
            executor = parent.executor

        if executor is None:
            self._executor = ThreadPoolExecutor(1,
                                                thread_name_prefix=self.__class__.__name__,
                                                initializer=init_actor_thread,
                                                initargs=(self,))
        else:
            self._executor = executor
            # Make sure that thread local variable is initialized
            self._executor.submit(init_actor_thread, self).result()

    def is_actor_thread(self):
        return getattr(self._thread_local, CORRECT_THREAD_ATTR, False)

    def run_on_executor(self, func, *args, timeout: float = None, force_schedule: bool = False, **kwargs):
        if timeout is not None and timeout > 0:
            # We need to wrap future that is going to be create after specified time passes
            future = Future()

            def wrapper(self: Actor, timer: threading.Timer, future: Future, func, args, kwargs):
                self._timers.remove(timer)
                if self._cancel_timers:
                    return

                try:
                    executor_future = self._executor.submit(func, *args, *kwargs)
                except Exception as exception:
                    future.set_exception(exception)
                    return

                def done_cb(future: Future, executor_future: Future):
                    assert not executor_future.running()

                    future.set_result(executor_future.result())
                    exception = executor_future.exception()
                    if exception:
                        future.set_exception(exception)

                executor_future.add_done_callback(functools.partial(done_cb, future))

            args = [self, None, future, func, args, kwargs]
            timer = threading.Timer(timeout, wrapper,
                                    args=args)
            args[1] = timer

            self._timers.add(timer)
            timer.daemon = True
            timer.start()
            return future

        if not self.is_actor_thread() or timeout is not None or force_schedule:
            return self._executor.submit(func, *args, *kwargs)

        future = Future()
        try:
            future.set_result(func(*args, *kwargs))
        except BaseException as exception:
            future.set_exception(exception)

        return future

    def run_guarded(self, func, *args, timeout=None, force_schedule=True, **kwargs):
        if self.is_guarded_pending(func):
            return

        self._guards.add(func)

        @functools.wraps(func)
        def wrapper(self: Actor, func, args, kwargs):
            self._guards.remove(func)
            func(*args, *kwargs)

        return self.run_on_executor(wrapper,
                                    self, func, args, kwargs,
                                    timeout=timeout, force_schedule=force_schedule)

    def is_guarded_pending(self, func):
        return func in self._guards

    @property
    def executor(self) -> ThreadPoolExecutor:
        return self._executor

    def __del__(self):
        self._cancel_timers = True
        for timer in self._timers:
            timer.cancel()
            timer.join()

        self._executor.shutdown()

    @staticmethod
    def handler(guarded=False, force_schedule=False):
        force_schedule_parent = force_schedule

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, timeout=None, force_schedule=False, **kwargs):
                self: Actor = args[0]
                force_schedule = force_schedule or force_schedule_parent

                if guarded:
                    return self.run_guarded(func,
                                            *args,
                                            timeout=timeout,
                                            force_schedule=force_schedule,
                                            **kwargs)
                else:
                    return self.run_on_executor(func,
                                                *args,
                                                timeout=timeout,
                                                force_schedule=force_schedule,
                                                **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def assert_executor(hard=False):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self: Actor = args[0]
                if not self.is_actor_thread():
                    logging.warning(f"{func} was called on invalid non-actor thread")
                    assert self.is_actor_thread()
                    if hard:
                        raise SystemError

                return func(*args, **kwargs)

            return wrapper

        return decorator
