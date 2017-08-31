import requests
import yaml
import configparser

class GroundClient:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.address = 'http://' + config['Ground']['url'] + ':' + str(config['Ground']['port'])


    def get_node(self, node_key):
        node_key = node_key.replace('/', '%2F')
        r = requests.get(self.address + '/nodes/' + node_key)

        return r.json()

    def get_node_version(self, nv_id):
        r = requests.get(self.address + '/versions/nodes/' + str(nv_id))

        return r.json()

    def create_node(self, node_key, node_name):
        node_key = node_key.replace('/', '%2F')
        node_name = node_name.replace('/', '%2F')

        url = self.address + '/nodes'
        r = requests.post(url, json = {'sourceKey': node_key, 'name': node_name})

        return r.json()

    def create_node_version(self, node_id, tags, parents, structure_id=-1):
        if structure_id == -1:
            r = requests.post(self.address + '/versions/nodes', json = {'nodeId': node_id, 'tags': tags, "parentIds": parents})
        else:
            r = requests.post(self.address + '/versions/nodes', json = {'structureVersionId': structure_id, 'nodeId': node_id, 'tags': tags, "parentIds": parents})

        return r.json()

    def get_node_latest(self, node_key):
        node_key = node_key.replace('/', '%2F')
        r = requests.get(self.address + '/nodes/' + node_key + '/latest')

        return r.json()

    def get_structure_latest(self, structure_key):
        r = requests.get(self.address + '/structures/' + structure_key + '/latest')

        return r.json()

    def get_structure(self, structure_key):
        r = requests.get(self.address + '/structures/' + structure_key)

        if r.status_code != 200:
            return None
        else:
            return r.json()

    def create_structure(self, structure_key, name):
        r = requests.post(self.address + '/structures', json = {'sourceKey': structure_key, 'name': name})

        return r.json()

    def create_structure_version(self, attributes, structure_id):
        r = requests.post(self.address + '/versions/structures', json = {'structureId': structure_id, 'attributes': attributes})

        return r.json()

    def create_lineage_edge(self, le_key, name):
        r = requests.post(self.address + '/lineage_edges', json = {'sourceKey': le_key, 'name': name})

        return r.json()

    def create_le_version(self, le_id, from_rv_id, to_rv_id, tags={}):
        r = requests.post(self.address + '/versions/lineage_edges', json = {'lineageEdgeId': le_id, 'fromRichVersionId': from_rv_id, 'toRichVersionId': to_rv_id, 'tags': tags})

        return r.json()

