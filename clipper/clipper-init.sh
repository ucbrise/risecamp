#!/bin/bash
set -e -x

if [[ "$CAMP_HOST" = "" ]]; then
  CAMP_HOST=$(python -c "import requests; print(requests.get('http://ip.42.pl/raw').text)")
fi

GRAFANA_URL="http://$CAMP_HOST/camp/clipper/grafana"
docker run --rm --name clipper-grafana --network clipper_network --label ai.clipper.container.label -d -e GF_DOMAIN="$IP" -e GF_SERVER_ROOT_URL="$GRAFANA_URL" grafana/grafana

mv /tmp/clipper.nginx.conf /etc/nginx/sites-enabled/default
service nginx restart
