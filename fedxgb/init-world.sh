#!/bin/bash

# This is an example startup script that performs critical initialization to
# prepare the container environment:

set -o errexit

service ssh start
echo "hello world!"
