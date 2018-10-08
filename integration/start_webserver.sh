#!/usr/bin/env bash

source activate pong_py2
url=`curl http://169.254.169.254/latest/meta-data/public-ipv4`
echo "Play Pong at $url/camp/integration/pong/"
python2 pong-js/pong-server.py $1
