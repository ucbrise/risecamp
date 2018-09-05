#!/bin/bash
set -o errexit

if [ "${NOTEBOOK_AUTH_TOKEN}" != "" ]; then
  echo "****"
  echo "**** Notebook Login URL: http://127.0.0.1:8888/${NOTEBOOK_BASE_URL}?token=${NOTEBOOK_AUTH_TOKEN}"
  echo "****"
  NOTEBOOK_FLAGS="${NOTEBOOK_FLAGS} --NotebookApp.token=\"${NOTEBOOK_AUTH_TOKEN}\""
fi

if [ "${NOTEBOOK_BASE_URL}" != "" ]; then
  NOTEBOOK_FLAGS="${NOTEBOOK_FLAGS} --NotebookApp.base_url=\"${NOTEBOOK_BASE_URL}\""
fi

# If individual projects need a script to run on startup they can
# add an ENV to the dockerfile
if [ "${PRE_START_SCRIPT}" != "" ]; then
  source ${PRE_START_SCRIPT}
fi

cd "/home/$NB_USER"
chown -R "$NB_USER:users" .
start-notebook.sh ${NOTEBOOK_FLAGS}
