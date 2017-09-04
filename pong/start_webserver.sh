#!/usr/bin/env bash

set -e
set -u
set -o pipefail

source activate clipper_py2 && python javascript-pong/pong-server.py $1
