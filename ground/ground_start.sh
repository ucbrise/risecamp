#!/bin/bash
sudo service postgresql start
tmux new-session -d 'cd ground-postgres-0.1.1 && bin/ground-postgres'
