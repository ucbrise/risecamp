#!/usr/bin/env bash

# From https://www.reddit.com/r/devops/comments/6d6dcu/connecting_to_localhost_of_the_machine_from/di0npw7/
echo $(netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}')
