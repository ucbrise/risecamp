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
    def onSetEntityResponse(self, response):
        self.assertEqual("okay", response.status)
        self.semaphore.release()

    def onSubscribeResponse(self, response):
        self.assertEqual("okay", response.status)
        self.semaphore.release()

    def onPublishResponse(self, response):
        self.assertEqual("okay", response.status)

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
        self.bw_client.asyncSetEntityFromFile(KEY_FILE, self.onSetEntityResponse)
        self.bw_client.overrideAutoChainTo(True)
        self.semaphore.acquire()
        self.bw_client.asyncSubscribe(URI, self.onSubscribeResponse, self.onMessage)
        self.semaphore.acquire()

    def tearDown(self):
        self.bw_client.close()

    def testPublishSubscribe(self):
        for msg in MESSAGES:
            po = PayloadObject((64, 0, 0, 0), None, msg)
            self.bw_client.asyncPublish(URI, self.onPublishResponse, payload_objects=(po,))
        self.semaphore.acquire()

if __name__ == "__main__":
    unittest.main()
