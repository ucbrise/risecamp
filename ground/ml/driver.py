import sys
import pprint
from time import sleep
from ground import GroundClient

original_schema = {
	"id" : {
		"key" : "id",
		"value" : "integer id of the tweet",
		"type" : "string"
	},
	"tweet" : {
		"key" : "tweet",
		"value" : "text of the tweet",
		"type" : "string"
	},
	"place" : {
		"key" : "place",
		"value" : "city state from which the tweet originated",
		"type" : "string"
	},
	"city" : {
		"key" : "city",
		"value" : "city from which the tweet originated",
		"type" : "string"
	},
	"country" : {
		"key" : "country",
		"value" : "country from which the tweet originated",
		"type" : "string"
	},
	"code": {
		"key" : "code",
		"value" : "two character country code",
		"type" : "string"
	},
	"training" : {
		"key" : "training",
		"value" : "boolean whether record is used for training",
		"type" : "string"
	}
}

alternative_schema = {
	"id" : {
		"key" : "id",
		"value" : "integer id of the tweet",
		"type" : "string"
	},
	"tweet" : {
		"key" : "tweet",
		"value" : "text of the tweet",
		"type" : "string"
	},
	"code" : {
		"key" : "code",
		"value" : "country from which the tweet originated",
		"type" : "string"
	},
	"city" : {
		"key" : "city",
		"value" : "city from which the tweet originated",
		"type" : "string"
	},
	"country" : {
		"key" : "country",
		"value" : "two character country code",
		"type" : "string"
	},
	"training" : {
		"key" : "training",
		"value" : "boolean whether record is used for training",
		"type" : "string"
	}
}

client = GroundClient()
pp = pprint.PrettyPrinter(indent=4)

def init():
	if "Error" in client.getNode("table_tweets"):
		client.createNode("table_tweets")
		itemId = client.getNode("table_tweets")["itemId"]
		client.createNodeVersion(itemId, tags=original_schema)

def update_bk():
	if len(client.getNodeVersionHistory("table_tweets")) < 2:
		latestNV = client.getNodeVersionLatest("table_tweets")
		itemId = client.getNode("table_tweets")["itemId"]
		client.createNodeVersion(itemId, tags=alternative_schema, parentIds=latestNV)

def update_fx():
	latestNV = client.getNodeVersionLatest("table_tweets")
	itemId = client.getNode("table_tweets")["itemId"]
	client.createNodeVersion(itemId, tags=original_schema, parentIds=latestNV)

def debug():
	# Prints the full path of node versions, starting at the root.
	nodeVersions = []
	nodeVersionHistory = client.getNodeVersionHistory("table_tweets")
	parent = '0'
	print ''
	print "History of table schema for tweets, ordered from oldest to latest."
	print ''
	while parent in nodeVersionHistory:
		child = str(nodeVersionHistory[parent])
		nodeVersion = client.getNodeVersion(child)
		pp.pprint(nodeVersion["tags"])
		print ''
		print ''
		nodeVersions.append(nodeVersion)
		parent = child
	return nodeVersions


def test_latest():
	print client.getNodeVersionLatest("table_tweets")

def test_history():
	print client.getNodeVersionHistory("table_tweets")

flag = sys.argv[1]
if flag == "i":
	init()
elif flag == "b":
	update_bk()
elif flag == "f":
	update_fx()
elif flag == "d":
	debug()
elif flag == "l":
	test_latest()
elif flag == "h":
	test_history()
