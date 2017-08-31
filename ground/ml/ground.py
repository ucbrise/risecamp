import requests, json, numpy as np

class GroundClient:
	
	headers = {"Content-type": "application/json"}
	
	def __init__(self, host='localhost', port=9000):
		self.host = host
		self.port = str(port)
		self.url = "http://" + self.host + ":" + self.port

	### EDGES ###
	def createEdge(self, sourceKey, fromNodeId, toNodeId, name="null"):
		d = {
			"sourceKey": sourceKey,
			"fromNodeId": fromNodeId,
			"toNodeId": toNodeId,
			"name": name
		}
		r = requests.post(self.url + "/edges", headers=self.headers, 
			data=json.dumps(d))
		return r.json()

	def createEdgeVersion(self, edgeId, toNodeVersionStartId):
		d = {
			"edgeId": edgeId,
			"toNodeVersionStartId": toNodeVersionStartId
		}
		r = requests.post(self.url + "/versions/edges", headers=self.headers,
			data=json.dumps(d))
		return r.json()

	def getEdge(self, sourceKey):
		return requests.get(self.url + "/edges/" + str(sourceKey)).json()

	def getEdgeVersion(self, edgeId):
		return requests.get(self.url + "/versions/edges" + str(edgeId)).json()

	### NODES ###
	def createNode(self, sourceKey, name="null"):
		d = {
			"sourceKey": sourceKey,
			"name": name
		}
		r = requests.post(self.url + "/nodes", headers=self.headers, 
			data=json.dumps(d))
		return r.json()

	def createNodeVersion(self, nodeId, tags=None, parentIds=None):
		d = {
			"nodeId": nodeId
		}
		if tags is not None:
			d["tags"] = tags
		if parentIds is not None:
			d["parentIds"] = parentIds
		r = requests.post(self.url + "/versions/nodes", headers=self.headers, 
			data=json.dumps(d))
		return r.json()

	def getNode(self, sourceKey):
		return requests.get(self.url + "/nodes/" + str(sourceKey)).json()

	def getNodeVersion(self, nodeId):
		return requests.get(self.url + "/versions/nodes/" + str(nodeId)).json()

	def getNodeVersionLatest(self, sourceKey):
		return requests.get(self.url + "/nodes/" + str(sourceKey) + "/latest").json()

	def getNodeVersionHistory(self, sourceKey):
		return requests.get(self.url + "/nodes/" + str(sourceKey) + "/history").json()

	### GRAPHS ###
	def createGraph(self, sourceKey, name="null"):
		d = {
			"sourceKey": sourceKey,
			"name": name
		}
		r = requests.post(self.url + "/graphs", headers=self.headers, 
			data=json.dumps(d))
		return r.json()

	def createGraphVersion(self, graphId, edgeVersionIds):
		d = {
			"graphId": graphId,
			"edgeVersionIds": edgeVersionIds
		}
		r = requests.post(self.url + "/versions/graphs", headers=self.headers,
			data=json.dumps(d))
		return r.json()

	def getGraph(self, sourceKey):
		return requests.get(self.url + "/graphs/" + str(sourceKey)).json()

	def getGraphVersion(self, graphId):
		return requests.get(self.url + "/versions/graphs/" + str(graphId)).json()


