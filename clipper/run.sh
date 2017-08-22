#!/usr/bin/env bash

docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -p 8888:8888 clipper/risecamp-exercises-2017
