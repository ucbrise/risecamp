#!/bin/bash
set -o errexit

NOTEBOOK_FLAGS="${NOTEBOOK_FLAGS} --NotebookApp.base_url=\"${CONTAINER_BASE_URL}/jupyter\""

if [ "${CONTAINER_AUTH_TOKEN}" != "" ]; then
  echo "****"
  echo "**** Notebook Login URL: http://127.0.0.1:8080/${CONTAINER_BASE_URL}?token=${CONTAINER_AUTH_TOKEN}"
  echo "****"
  NOTEBOOK_FLAGS="${NOTEBOOK_FLAGS} --NotebookApp.token=\"${CONTAINER_AUTH_TOKEN}\""
fi


IP=$(python -c "import requests; print(requests.get('http://ip.42.pl/raw').text)")
GRAFANA_URL="http://"+IP+"/camp/clipper/grafana"
docker stop clipper-grafana || true && docker rm clipper-grafana || true
docker run --rm --name clipper-grafana --network clipper_network -d -e GF_DOMAIN=$IP -e GF_SERVER_ROOT_URL=$GRAFANA_URL grafana/grafana
nginx -t

chgrp docker /var/run/docker.sock
service nginx start

cd "/home/$NB_USER"
chown -R "$NB_USER:users" .
start-notebook.sh ${NOTEBOOK_FLAGS}
