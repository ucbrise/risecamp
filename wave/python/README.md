# Simplified BW2 Client


```python
from client import get_client

c = get_client()
# defaults
#c = get_client(agent='$BW2_AGENT', entity='$BW2_DEFAULT_ENTITY')
# override
#c = get_client(agent='127.0.0.1:28589', entity='myentity.ent')

def cb(msg):
    # automatically unmarshalled
    print msg.payload
    if 'air_temp' in msg:
        print msg['air_temp']
    c.publish('scratch.ns/air_temp_mirror', (2,0,0,1), {'temp': air_temp})

c.subscribe('ciee/*/operative', cb)

# optional ponum filter; else takes first payload object
c.subscribe('ciee/*/operative', cb, '2.0.0.0/8')
```

Features:
- unique callbacks per subscription uri:
    - generally limiting, but helpful for ipython notebooks because
      you can re-run the cell and have the updated callback w/o having
      to worry about cancelling any previous subscriptions
- single payload object per message
- automatic unmarshalling of json, msgpack and string (`65.0.0.0/8`, `2.0.0.0/8` and `64.0.0.0/8`)
