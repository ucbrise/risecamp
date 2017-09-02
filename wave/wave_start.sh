#!/bin/bash

daemon --name ragent --respawn -- /bin/ragent client /etc/rise_entity.ent ragent.cal-sdb.org:28590 MT3dKUYB8cnIfsbnPrrgy8Cb_8whVKM-Gtg2qd79Xco= 0.0.0.0:28589
python2 /usr/local/bin/getentity.py
rm -f .bw2bind.log
