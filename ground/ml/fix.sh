#!/bin/bash
psql risecamp -U ground -f fix.sql && \
python driver.py f && \
touch crawler.py;