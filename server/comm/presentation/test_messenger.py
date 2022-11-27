import logging
import unittest
from queue import Empty, Queue
from typing import List

from .messenger import IMessageClient, IOutgoingMessage
from .protocol_messenger import ProtocolMessenger
from .protocol_pb2 import GenericMessage, TestMessage
from ..transport.test_transport import LoopbackTransport

from ..transport.transport import Transport, ConnectionState


class MessageLoopbackTest(unittest.TestCase):
    @staticmethod
    def setUpClass(**kwargs) -> None:
        import sys

        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    def test_loopback_send_received(self):
        test_self = self
        queue: Queue[GenericMessage] = Queue()

        class Client(IMessageClient):
            def on_message_received(self, message: GenericMessage):
                logging.debug(f"on_packet_received(): packet={message}")
                queue.put(message)

            def on_state_changed(self, state: ConnectionState):
                pass

            def on_error(self):
                nonlocal test_self
                test_self.fail("on_error():")

        client = Client()
        messenger = ProtocolMessenger.Builder(
            transport=Transport.Builder(transport=LoopbackTransport.Builder())
        ).build(client)
        messages: List[IOutgoingMessage] = []

        for i in range(10):
            msg = GenericMessage(
                sessionId=i, request=i, test=TestMessage(
                    value=f"Test message {i}")
            )
            logging.info(f"test: Sending {msg}")
            messages.append(messenger.send(msg))

        for message in messages:
            received: GenericMessage = queue.get(timeout=5.0)

            self.assertIsNotNone(received)
            logging.info(f"test: Dequeued {received}")
            self.assertEqual(received, message.message)

        try:
            queue.get(timeout=1.0)
            self.fail("Received more messages then expected")
        except Empty:
            pass


if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    unittest.main()
