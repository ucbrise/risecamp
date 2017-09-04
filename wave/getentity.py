import requests
import socket
import base64
import os


hostname = socket.getfqdn()
resp = requests.get("http://api.cal-sdb.org/faucet?id={0}".format(hostname))
if not resp.ok:
    raise Exception(resp.json().get("message"))
msg = resp.json()
lightEntity = base64.b64decode(msg["lightEntity"])
switchEntity = base64.b64decode(msg["switchEntity"])
namespaceEntity = base64.b64decode(msg["namespaceEntity"])
user = os.environ["NB_USER"]
with open('/home/{0}/wave/light.ent'.format(user),'wb') as f:
    print 'Saved light entity to light.ent'
    f.write(lightEntity)
with open('/home/{0}/wave/switch.ent'.format(user),'wb') as f:
    print 'Saved switch entity to switch.ent'
    f.write(switchEntity)
with open('/home/{0}/wave/ns.ent'.format(user),'wb') as f:
    print 'Saved namespace entity to ns.ent'
    f.write(namespaceEntity)
