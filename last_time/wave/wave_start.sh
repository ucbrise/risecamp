#!/bin/bash
set -e

daemon --name ragent --respawn -- /bin/ragent client /etc/rise_entity.ent ragent.cal-sdb.org:28590 MT3dKUYB8cnIfsbnPrrgy8Cb_8whVKM-Gtg2qd79Xco= 0.0.0.0:28589
python2 /usr/local/bin/getentity.py
export BW2_DEFAULT_BANKROLL="/home/$NB_USER/wave/ns.ent"
export BW2_DEFAULT_ENTITY="/home/$NB_USER/wave/ns.ent"
export NAMESPACE=$(bw2 i /home/$NB_USER/wave/ns.ent | awk '{if($2~"Alias") print $3}')
rm -f .bw2bind.log
