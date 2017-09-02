#!/bin/bash
sudo service postgresql start
tmux new-session -d 'cd ground-0.1.2 && bin/ground-postgres'

if [ "$SKIP_NOTEBOOK" == "" ]; then
  echo "Starting the notebook server"
  start-notebook.sh
fi
