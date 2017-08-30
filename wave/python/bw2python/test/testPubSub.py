import unittest

from bw2python.bwtypes import PayloadObject
from bw2python.client import Client
from threading import Semaphore

MESSAGES = [
    "Hello, world!",
    "Bosswave 2",
    "Lorem ipsum",
    "dolor sit amet"
]

URI = "scratch.ns/unittests/python"
KEY_FILE = "unitTests.key"

class TestPubSubscribe(unittest.TestCase):
    def onMessage(self, message):
        self.assertTrue(len(message.payload_objects) > 0)
        msg_body = message.payload_objects[0].content
        self.assertIn(msg_body, MESSAGES)
        self.counter += 1
        if self.counter == len(MESSAGES):
            self.semaphore.release()

    def setUp(self):
        self.counter = 0
        self.semaphore = Semaphore(0)
        self.bw_client = Client()
        self.bw_client.setEntityFromFile(KEY_FILE)
        self.bw_client.overrideAutoChainTo(True)
        self.bw_client.subscribe(URI, self.onMessage)

    def tearDown(self):
        self.bw_client.close()

    def testPublishSubscribe(self):
        for msg in MESSAGES:
            po = PayloadObject((64, 0, 0, 0), None, msg)
            self.bw_client.publish(URI, payload_objects=(po,))
        self.semaphore.acquire()

if __name__ == "__main__":
    unittest.main()
