#!/usr/bin/env bash

docker run -d -v /var/run/docker.sock:/var/run/docker.sock -p 8888:8888 -p 1337:1337 clipper/risecamp-exercises
