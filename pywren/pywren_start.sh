#!/bin/bash
cd /opt/pywren
python config_encoder.py decode $PYWREN_CONFIG_STRING /home/$NB_USER/.pywren_config
chmod a+r /home/$NB_USER/.pywren_config
export PYWREN_LOGLEVEL=ERROR
pywren deploy_lambda
