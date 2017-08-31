#!/bin/bash
set -e

./ground/ground_start.sh &
/opt/pywren/pywren_start.sh &
source ./wave/wave_start.sh

start-notebook.sh
