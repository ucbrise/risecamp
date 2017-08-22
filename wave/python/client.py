from bw2python import ponames
from bw2python.client import Client as BW2Client
from bw2python.bwtypes import PayloadObject
import msgpack
import time
import json
import os

# keepalive when the client starts
import threading
import socket
hostname = socket.getfqdn()
_client = None
def _keepalive():
    global _client
    while True:
        if _client is not None:
            _client.publish('scratch.ns/risealive', (64,0,0,0), hostname)
        time.sleep(30)
_keepalive_worker = threading.Thread(target=_keepalive)
_keepalive_worker.daemon = True
_keepalive_worker.start()


def once(func):
    def execute(*args, **kwargs):
        if not execute.already_run:
            execute.already_run = True
            func(*args, **kwargs)
    execute.already_run = False
    return execute
    

def get_client(agent=None, entity=None):
    # set defaults
    if agent is None:
        agent = os.environ.get('BW2_AGENT','127.0.0.1:28589')
    if entity is None:
        entity = os.environ.get('BW2_DEFAULT_ENTITY','/etc/rise_entity.ent')

    if agent is None:
        raise Exception("Need to provide an agent or set BW2_AGENT")
    if entity is None:
        raise Exception("Need to provide an entity or set BW2_DEFAULT_ENTITY")

    hostname, port = agent.split(':')
    c = Client(hostname, port, entity)

    # hack for the keepalive above
    global _client
    _client = c
    return c

def unmarshal(po):
    """
    Unmarshal payload object into Python object using payload number
    """
    if po.type_dotted[0] == 2:
        return msgpack.unpackb(po.content)
    if po.type_dotted[0] == 64:
        return str(po.content)
    if po.type_dotted[0] == 65:
        return json.loads(str(po.content))
    return po.content

def marshal(ponum, msg):
    if ponum[0] == 2:
        return msgpack.packb(msg)
    if ponum[0] == 64:
        return str(msg)
    if ponum[0] == 65:
        return json.dumps(msg)
    return str(msg)

def get_ponum_and_mask(ponum):
    parts = ponum.split('/')
    if len(parts) != 2:
        mask = 32
    else:
        mask = int(parts[1])
    type_dotted = map(int, parts[0].split('.'))
    octet_val = (type_dotted[0] << 24) + (type_dotted[1] << 16) +\
                 (type_dotted[2] << 8) + type_dotted[3]
    return octet_val, mask


def istype(type_dotted, tocheck_dotform):
    ponum = (type_dotted[0] << 24) + (type_dotted[1] << 16) +\
             (type_dotted[2] << 8) + type_dotted[3]
    tocheck, mask = get_ponum_and_mask(tocheck_dotform)
    return (ponum >> (32-mask)) == (tocheck >> (32-mask))
    

class Client(BW2Client):
    
    def __init__(self, hostname, port, entity):
        super(Client, self).__init__(hostname, int(port))
        self.setEntityFromFile(entity)
        self.overrideAutoChainTo(True)
        self._subs = {}

    def subscribe(self, uri, handler, ponum=None):
        def cb(msg):
            handler = self._subs[uri]
            if len(msg.payload_objects) == 0:
                handler(msg)
                return
            if ponum is None:
                msg.payload = unmarshal(msg.payload_objects[0])
                handler(msg)
                return 
            for po in msg.payload_objects:
                if istype(po.type_dotted, ponum):
                    msg.payload = unmarshal(po)
                    handler(msg)
                return
        if self._subs.get(uri) is None:
            super(Client, self).subscribe(uri, cb)
        self._subs[uri] = handler

    def publish(self, uri, ponum, msg):
        po = PayloadObject(ponum, None, marshal(ponum, msg)) 
        super(Client, self).publish(uri, payload_objects=(po,))

if __name__ == '__main__':
    c = get_client()
    def cb(msg):
        print msg.payload
        c.publish('scratch.ns/abc',(2,0,0,1), {'abc': 123})
    c.subscribe("ciee/*", cb, "2.0.0.0/8")
    import time
    while True:
        time.sleep(100)
