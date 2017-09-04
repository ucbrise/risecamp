#!/bin/bash
cd /opt/pywren
python config_encoder.py decode $PYWREN_CONFIG_STRING ~/.pywren_config
export PYWREN_LOGLEVEL=ERROR
pywren deploy_lambda
