#!/bin/bash

./ground/ground_start.sh
/opt/pywren/pywren_start.sh
./wave/wave_start.sh

export BW2_DEFAULT_BANKROLL="/home/$NB_USER/wave/ns.ent"
export BW2_DEFAULT_ENTITY="/home/$NB_USER/wave/ns.ent"
export NAMESPACE=$(bw2 i /home/$NB_USER/wave/ns.ent | awk '{if($2~"Alias") print $3}')

cd /home/$NB_USER
start-notebook.sh
