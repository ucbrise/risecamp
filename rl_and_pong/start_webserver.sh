#!/usr/bin/env bash

source activate clipper_py2
url=`curl http://169.254.169.254/latest/meta-data/public-ipv4`
echo "Play Pong at $url/pong/"
python javascript-pong/pong-server.py $1
