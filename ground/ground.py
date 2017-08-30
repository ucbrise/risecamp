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

    def create_node_version(self, node_id, tags, parents):
        r = requests.post(self.address + '/versions/nodes', json = {'nodeId': node_id, 'tags': tags, "parentIds": parents})

        return r.json()

    def get_latest(self, node_key):
        node_key = node_key.replace('/', '%2F')
        r = requests.get(self.address + '/nodes/' + node_key + '/latest')

        return r.json()
