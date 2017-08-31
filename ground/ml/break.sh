#!/bin/bash
psql risecamp -U ground -f break.sql && \
python driver.py b && \
touch crawler.py