#!/usr/bin/env bash

docker run --rm --network=host -v /var/run/docker.sock:/var/run/docker.sock \
  -p 8888:8888 risecamp/clipper-exercise:test
