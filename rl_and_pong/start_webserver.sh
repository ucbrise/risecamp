#!/usr/bin/env bash

source activate clipper_py2
url=`curl -s http://169.254.169.254/latest/meta-data/public-ipv4`
if [ -z "$url" ]; then
  url="localhost"
fi
echo "Play Pong at http://$url:3000/pong/"
python javascript-pong/pong-server.py $1
