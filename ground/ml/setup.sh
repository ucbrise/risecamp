#!/bin/bash
sudo pip install psycopg2
sudo pip install requests
sudo pip install numpy
sudo pip install pandas
sudo pip install tweet_preprocessor
sudo pip install scipy
sudo pip install -U scikit-learn

dropdb risecamp;
createdb risecamp;
psql -U ground -c "update pg_database set encoding = pg_char_to_encoding('UTF8') where datname = 'risecamp'"
psql -U ground risecamp < risecamp.out;
psql -U ground risecamp -f permissions.sql;

python driver.py i;

sudo cp my_cleaner_default.py my_cleaner.py
