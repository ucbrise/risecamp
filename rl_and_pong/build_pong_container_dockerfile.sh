#!/usr/bin/env bash

image_name="clipper/risecamp-pong-container"
docker build -t $image_name -f PongPolicyDockerfile .
docker push $image_name
