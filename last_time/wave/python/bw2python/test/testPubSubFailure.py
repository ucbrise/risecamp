import unittest

from bw2python import ponames
from bw2python.bwtypes import PayloadObject
from bw2python.client import Client

MESSAGES = [
    "Hello, world!",
    "Bosswave 2",
    "Lorem ipsum",
    "dolor sit amet"
]

URI = "scratch.ns/unittests/python"
KEY_FILE = "unitTests.key"

class TestPubSubFailure(unittest.TestCase):
    def onMessage(self, message):
        pass

    def setUp(self):
        self.bw_client = Client()
        self.bw_client.setEntityFromFile(KEY_FILE)
        self.bw_client.overrideAutoChainTo(True)

    def tearDown(self):
        self.bw_client.close()

    def testSubscribeFailure(self):
        with self.assertRaises(RuntimeError):
            # Unit test key should not have permissions on this URI
            self.bw_client.subscribe("jkolb/test", self.onMessage)

    def testPublishFailure(self):
        with self.assertRaises(RuntimeError):
            # Unit test key should not have permissions on this URI
            po = PayloadObject(ponames.PODFText, None, "Hello, World!")
            self.bw_client.publish("jkolb/test", payload_objects=(po,))

if __name__ == "__main__":
    unittest.main()
