#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

set -e

# Handle special flags if we're root
if [ $(id -u) == 0 ] ; then
    # run the ragent in the background
    daemon --name ragent --respawn -- /bin/ragent client /etc/rise_entity.ent ragent.cal-sdb.org:28590 MT3dKUYB8cnIfsbnPrrgy8Cb_8whVKM-Gtg2qd79Xco= 0.0.0.0:28589
    python2 /usr/local/bin/getentity.py
    export BW2_DEFAULT_BANKROLL="/home/$NB_USER/ns.ent"
    export BW2_DEFAULT_ENTITY="/home/$NB_USER/ns.ent"
    export NAMESPACE=$(bw2 i /home/$NB_USER/ns.ent | awk '{if($2~"Alias") print $3}')
    rm -f .bw2bind.log
    # Handle username change. Since this is cheap, do this unconditionally
    usermod -d /home/$NB_USER -l $NB_USER jovyan

    # Change UID of NB_USER to NB_UID if it does not match
    if [ "$NB_UID" != $(id -u $NB_USER) ] ; then
        echo "Set user UID to: $NB_UID"
        usermod -u $NB_UID $NB_USER
        # Careful: $HOME might resolve to /root depending on how the
        # container is started. Use the $NB_USER home path explicitly.
        for d in "$CONDA_DIR" "$JULIA_PKGDIR" "/home/$NB_USER"; do
            if [[ ! -z "$d" && -d "$d" ]]; then
                echo "Set ownership to uid $NB_UID: $d"
                chown -R $NB_UID "$d"
            fi
        done
    fi

    # Change GID of NB_USER to NB_GID if NB_GID is passed as a parameter
    if [ "$NB_GID" ] ; then
        echo "Change GID to $NB_GID"
        groupmod -g $NB_GID -o $(id -g -n $NB_USER)
    fi

    # Enable sudo if requested
    if [[ "$GRANT_SUDO" == "1" || "$GRANT_SUDO" == 'yes' ]]; then
        echo "Granting $NB_USER sudo access"
        echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
    fi

    # Exec the command as NB_USER
    echo "Execute the command as $NB_USER"
    exec su $NB_USER -c "env PATH=$PATH $*"
else
  echo 'Container must be run as root for stuffs'
  exit 1
fi
