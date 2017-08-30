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
    def setUp(self):
        self.bw_client = Client()
        self.bw_client.setEntityFromFile(KEY_FILE)
        self.bw_client.overrideAutoChainTo(True)

    def tearDown(self):
        self.bw_client.close()

    def testListQuery(self):
        for planet, probe in PERSISTED_DATA.items():
            po = PayloadObject((64, 0, 0, 0), None, probe)
            uri = BASE_URI + "/persisted/" + planet
            self.bw_client.publish(uri, payload_objects=(po,), persist=True)

        results = self.bw_client.query(BASE_URI + "/persisted/+")
        self.assertEquals(len(results), len(PERSISTED_DATA))
        probes = [result.payload_objects[0].content for result in results]
        self.assertTrue(all([probe in PERSISTED_DATA.values() for probe in probes]))

        children = self.bw_client.list(BASE_URI + "/persisted")
        self.assertEquals(len(children), len(PERSISTED_DATA))
        planets = [child[child.rfind("/")+1:] for child in children]
        self.assertTrue(all([planet in PERSISTED_DATA.keys() for planet in planets]))

if __name__ == "__main__":
    unittest.main()
