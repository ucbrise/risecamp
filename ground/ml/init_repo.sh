#!/bin/bash

rm -rf .git/
git init

git config user.email "risecampuser@berkeley.edu"
git config user.name "RISE Camp User"

git add .
git commit -m "Initial commit"
