#! /bin/bash
PGPASSWORD=metadata psql -U ground risecamp -f break.sql;
python driver.py b;