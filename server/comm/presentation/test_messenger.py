import unittest
from queue import Empty, Queue

from server.comm.presentation.messenger import IMessageClient
from server.comm.presentation.protocol_messenger import ProtocolMessenger
from server.comm.presentation.protocol_pb2 import GenericMessage, TestMessage
from server.comm.transport.test_transport import LoopbackTransport
from server.comm.transport.transport import *


class MessageLoopbackTest(unittest.TestCase):

    @staticmethod
    def setUpClass() -> None:
        import sys
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    def test_loopback_send_received(self):
        test_self = self
        queue = Queue()

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
        transport = ProtocolMessenger(lambda client: Transport(LoopbackTransport, client), client)
        messages = []

        for i in range(10):
            message = GenericMessage(sessionId=i, request=i, test=TestMessage(value=f"Test message {i}"))
            logging.info(f"test: Sending {message}")
            messages.append(transport.send(message))

        for message in messages:
            received: bytes = queue.get()  # timeout=5.0)

            self.assertIsNotNone(received)
            logging.info(f"test: Dequeued {received}")
            self.assertEqual(received, message.message)

        try:
            queue.get(timeout=1.0)
            self.fail("Received more messages then expected")
        except Empty:
            pass


if __name__ == '__main__':
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    unittest.main()
