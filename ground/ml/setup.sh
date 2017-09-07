#!/bin/bash

# reset ground db; this is to make sure it doesn't break if run multiple times
bash $NB_GROUND_HOME/reset_ground.sh

# init git repo
bash init_repo.sh
python register_repo.py

# drop and recreate the risecamp db
dropdb --if-exists risecamp;
createdb risecamp;

# add data and permissions to the risecamp db
psql -U ground -c "update pg_database set encoding = pg_char_to_encoding('UTF8') where datname = 'risecamp'"
psql -U ground risecamp < risecamp.out;
psql -U ground risecamp -f permissions.sql;

# register info with the driver
python driver.py i;
