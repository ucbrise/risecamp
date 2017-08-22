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
    def setUp(self):
        self.bw_client = Client()
        self.bw_client.setEntityFromFile(KEY_FILE)
        self.bw_client.overrideAutoChainTo(True)

    def tearDown(self):
        self.bw_client.close()

    def testQueryFailure(self):
        with self.assertRaises(RuntimeError):
            # Unit test key should not have permissions on this URI
            self.bw_client.query("jkolb/test")

    def testListFailure(self):
        with self.assertRaises(RuntimeError):
            # Unit test key should not have permissions on this URI
            self.bw_client.list("jkolb/test")

if __name__ == "__main__":
    unittest.main()
