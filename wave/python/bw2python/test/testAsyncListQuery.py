import unittest

from bw2python.bwtypes import PayloadObject
from bw2python.client import Client
from threading import Semaphore

BASE_URI = "scratch.ns/unittests/python"
KEY_FILE = "unitTests.key"

PERSISTED_DATA = {
    "Mercury" : "Messenger",
    "Venus"   : "Venera",
    "Mars"    : "Pathfinder",
    "Jupiter" : "Galileo",
    "Saturn"  : "Cassini",
    "Pluto"   : "New Horizons",
}

class TestListQuery(unittest.TestCase):
    def onSetEntityResponse(self, response):
        self.assertEqual("okay", response.status)
        self.semaphore.release()

    def assertOkay(self, response):
        self.assertEqual("okay", response.status)

    def onMessage(self, message):
        if message.getFirstValue("finished") != "true":
            self.assertTrue(len(message.payload_objects) > 0)
            msg_body = message.payload_objects[0].content
            self.assertIn(msg_body, PERSISTED_DATA.values())
            self.counter += 1
        else:
            self.assertEqual(self.counter, len(PERSISTED_DATA))
            self.semaphore.release()

    def onListResult(self, child):
        if child is not None:
            planet = child[child.rfind("/")+1:]
            self.assertIn(planet, PERSISTED_DATA.keys())
            self.counter += 1
        else:
            self.assertEqual(self.counter, len(PERSISTED_DATA))
            self.semaphore.release()

    def setUp(self):
        self.counter = 0
        self.semaphore = Semaphore(0)
        self.bw_client = Client()
        self.bw_client.asyncSetEntityFromFile(KEY_FILE, self.onSetEntityResponse)
        self.bw_client.overrideAutoChainTo(True)
        self.semaphore.acquire()

    def tearDown(self):
        self.bw_client.close()

    def testListQuery(self):
        for planet, probe in PERSISTED_DATA.items():
            po = PayloadObject((64, 0, 0, 0), None, probe)
            uri = BASE_URI + "/persisted/" + planet
            self.bw_client.asyncPublish(uri, self.assertOkay, payload_objects=(po,), persist=True)
        self.bw_client.asyncQuery(BASE_URI + "/persisted/+", self.assertOkay, self.onMessage)
        self.semaphore.acquire()

        self.counter = 0
        self.bw_client.asyncList(BASE_URI + "/persisted", self.assertOkay, self.onListResult)
        self.semaphore.acquire()

if __name__ == "__main__":
    unittest.main()
