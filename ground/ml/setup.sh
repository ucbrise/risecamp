#!/bin/bash
dropdb risecamp;
createdb risecamp;
psql -U ground -c "update pg_database set encoding = pg_char_to_encoding('UTF8') where datname = 'risecamp'"
psql -U ground risecamp < risecamp.out;
psql -U ground risecamp -f permissions.sql;

python driver.py i;

cp my_cleaner_default.py my_cleaner.py
