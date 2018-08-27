#!/bin/bash

if [ "${NOTEBOOK_AUTH_TOKEN}" != "" ]; then
  echo "*** Auth Token: ${NOTEBOOK_AUTH_TOKEN}"
  NOTEBOOK_FLAGS="${NOTEBOOK_FLAGS} --NotebookApp.token=\"${NOTEBOOK_AUTH_TOKEN}\""
fi

if [ "${NOTEBOOK_BASE_URL}" != "" ]; then
  echo "*** Base URL: ${NOTEBOOK_BASE_URL}"
  NOTEBOOK_FLAGS="${NOTEBOOK_FLAGS} --NotebookApp.base_url=\"${NOTEBOOK_BASE_URL}\""
fi

cd /home/$NB_USER
start-notebook.sh ${NOTEBOOK_FLAGS}
