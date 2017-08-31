#!/usr/bin/env python
import os.path
import sys
import psycopg2
import csv
from credentials import connection_string

abspath = os.path.dirname(os.path.abspath(__file__))
flag = sys.argv[1]

try:
	conn = psycopg2.connect(connection_string)
except:
	print("I am unable to connect to the database.")

cur = conn.cursor()
if flag == "tr":
	cur.execute("""SELECT id, tweet, code, city, country FROM tweets where training = TRUE;""")
	rows = cur.fetchall()
	with open(abspath + "/training_tweets.csv", "w") as out:
		csv_out = csv.writer(out)
		for row in rows:
			csv_out.writerow(row)
if flag == "te":
	cur.execute("""SELECT id, tweet, code, city, country FROM tweets where training = FALSE;""")
	rows = cur.fetchall()
	with open(abspath + "/testing_tweets.csv", "w") as out:
		csv_out = csv.writer(out)
		for row in rows:
			csv_out.writerow(row)
