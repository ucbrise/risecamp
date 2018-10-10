#!/bin/bash
set -o errexit

NOTEBOOK_FLAGS="${NOTEBOOK_FLAGS} --NotebookApp.base_url=\"${CONTAINER_BASE_URL}/jupyter\""

if [ "${CONTAINER_AUTH_TOKEN}" != "" ]; then
  echo "****"
  echo "**** Notebook Login URL: http://127.0.0.1:8080/${CONTAINER_BASE_URL}?token=${CONTAINER_AUTH_TOKEN}"
  echo "****"
  NOTEBOOK_FLAGS="${NOTEBOOK_FLAGS} --NotebookApp.token=\"${CONTAINER_AUTH_TOKEN}\""
fi

chgrp docker /var/run/docker.sock
service nginx start

cd "/home/$NB_USER"
chown -R "$NB_USER:users" .
start-notebook.sh ${NOTEBOOK_FLAGS}
