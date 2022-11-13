import logging
import math
import threading
import time
import unittest
from queue import Queue, Empty

from server.actor import Actor


class ActorTests(unittest.TestCase):
    @staticmethod
    def setUpClass() -> None:
        import sys

        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    def setUp(self) -> None:
        self.tester = ActorTests.Tester()

    def tearDown(self) -> None:
        queue = self.tester.queue
        self.assertTrue(queue.empty())
        del self.tester
        self.assertTrue(queue.empty())

        try:
            queue.get(timeout=3)
            self.fail("Should raised Empty")
        except Empty:
            pass

    def test_not_guarded_simple(self):
        value = "test_not_guarded_simple"
        self.tester.not_guarded(value)
        self.assertIs(value, self.tester.queue.get(timeout=1.0))

    def test_guarded_simple(self):
        value = "test_guarded_simple"
        self.tester.guarded(value)
        self.assertIs(value, self.tester.queue.get(timeout=1.0))

    def test_asserted(self):
        value = "test_asserted"
        try:
            self.tester.asserted(value)
            self.fail("Should fail with not run on proper thread")
        except (AssertionError, SystemError):
            pass

    def test_single_timeout(self):
        duration = 5.0

        value = "test_single_timeout"
        start = time.monotonic()
        self.tester.not_guarded(value, timeout=duration)
        returned = self.tester.queue.get()
        end = time.monotonic()

        measured = end - start
        self.assertIs(value, returned)
        self.assertLess(math.fabs(duration - measured), 0.5)

    def test_not_guarded_count(self):
        value = "test_not_guarded_count"

        self.tester.busy_task()

        for i in range(10):
            self.tester.not_guarded(value)

        self.tester.event.set()

        for i in range(10):
            self.assertIs(value, self.tester.queue.get(timeout=3.0))

    def test_guarded_count(self):
        value = "test_guarded_count"

        self.tester.busy_task()

        for i in range(10):
            self.tester.guarded(value)

        self.tester.event.set()

        self.assertIs(value, self.tester.queue.get(timeout=3.0))

    def test_using_asserted(self):
        value = "test_using_asserted"

        self.tester.use_asserted(value)
        self.assertIs(value, self.tester.queue.get(timeout=1.0))

    def test_using_other_not_guarded(self):
        value = "test_using_other_not_guarded"
        amount = 10

        self.tester.use_other_not_guarded(self, amount, value)
        for _ in range(amount):
            self.assertIs(value, self.tester.queue.get(timeout=1.0))

    def test_using_other_guarded(self):
        value = "test_using_other_guarded"
        amount = 10

        self.tester.use_other_guarded(self, amount, value)
        for _ in range(amount):
            self.assertIs(value, self.tester.queue.get(timeout=1.0))

    class Tester(Actor):
        def __init__(self):
            super().__init__()
            self.queue: Queue[str] = Queue()
            self.event = threading.Event()

        @Actor.handler()
        def busy_task(self):
            logging.debug("busy_task():")
            self.event.wait()
            self.event.clear()

        @Actor.handler(guarded=False)
        def not_guarded(self, value):
            logging.debug(f"not_guarded(): value={value}")
            self.queue.put(value)

        @Actor.handler(guarded=True)
        def guarded(self, value):
            logging.debug(f"guarded(): value={value}")
            self.queue.put(value)

        @Actor.assert_executor()
        def asserted(self, value):
            logging.debug(f"asserted(): value={value}")
            self.queue.put(value)

        @Actor.handler()
        def use_asserted(self, value):
            logging.debug(f"use_asserted(): value={value}")
            self.asserted(value)

        @Actor.handler(guarded=False)
        def use_other_not_guarded(self, actor_tests: "ActorTests", amount,
                                  value):
            logging.debug(f"use_other_not_guarded(): value={value}")
            for _ in range(amount):
                actor_tests.assertTrue(self.not_guarded(value).done())

        @Actor.handler(guarded=True)
        def use_other_guarded(self, actor_tests: "ActorTests", amount, value):
            logging.debug(f"use_other_guarded(): value={value}")
            for _ in range(amount):
                actor_tests.assertTrue(self.guarded(value).done())


if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(asctime)s,%(msecs)d %(levelname)-8s "
                        "[%(filename)s:%(lineno)d] %(message)s")
    unittest.main()
