#!/bin/bash

cd ground && ./ground_start.sh && cd ..
/opt/pywren/pywren_start.sh &

# an enhanced kludge to ensure clipper successfully call docker.sock
# https://stackoverflow.com/questions/23544282/what-is-the-best-way-to-manage-permissions-for-docker-shared-volumes/28596874#28596874
TARGET_GID=$(stat -c "%g" /var/run/docker.sock)

EXISTS=$(cat /etc/group | cut -d: -f3 | grep "^${TARGET_GID}\$" | wc -l)

# Create new group using target GID and add user
if [ $EXISTS == "0" ]; then
  groupadd -g $TARGET_GID risecampdocker
  gpasswd -a $NB_USER risecampdocker
else
  # GID exists, find group name and add
  GROUP=$(getent group $TARGET_GID | cut -d: -f1)
  gpasswd -a $NB_USER $GROUP
fi

./wave/wave_start.sh
export BW2_DEFAULT_BANKROLL="/home/$NB_USER/wave/ns.ent"
export BW2_DEFAULT_ENTITY="/home/$NB_USER/wave/ns.ent"
export NAMESPACE=$(bw2 i /home/$NB_USER/wave/ns.ent | awk '{if($2~"Alias") print $3}')

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
