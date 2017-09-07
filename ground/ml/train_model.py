#!/usr/bin/env python
""" train_model.py
To run:
    train_model.py

Output:
    intermediary.pkl

intermediary.pkl is a python dictionary with the following keys, values:
{
    "vectorizer" : a scikit-learn vectorizer for text data,
    "country_dict" : a dictionary for converting between country code and integer,
    "classifier" : a scikit-learn classifier (multinomial-naive-bayes)
}

"""
import pandas as pd
import numpy as np
import os, pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from shared import params, relevant_attributes

from ground.client import GroundClient

abspath = os.path.dirname(os.path.abspath(__file__))
intermediary = {}

with open(abspath + '/clean_training_tweets.pkl', 'rb') as f:
    tweet_df = pickle.load(f)

# Select a relevant subset of features
tweet_df = tweet_df[relevant_attributes]

# Convert string country code to integer country code
country_codes = set([i for i in tweet_df["code"]])
country_dict = {}
for idx, code in enumerate(country_codes):
    country_dict[code] = idx
intermediary["country_dict"] = country_dict

def convert_to_int(country_string):
    return country_dict[country_string]

tweet_df["code"] = tweet_df["code"].apply(convert_to_int)

## Convert tweet to bag of words for learning

# Tokenize Text
count_vect = CountVectorizer()
X_train = count_vect.fit_transform(tweet_df["tweet"])

intermediary["vectorizer"] = count_vect

X_train_label = np.array(tweet_df["code"])

# Train a classifier
clf = MultinomialNB().fit(X_train, X_train_label)

intermediary["classifier"] = clf

with open(abspath + '/intermediary.pkl', 'wb') as f:
    pickle.dump(intermediary, f, protocol = 2)

'''
REGISTER MODEL INFO WITH GROUND
'''
gc = GroundClient()

# get the latest git commit in Ground
latest_git_version = gc.getNodeLatestVersions("ml_repo")[0]

# check if the model node already exists; if so, get the latest version of it
# else create it
node = gc.getNode("model")
parents = []
node_id = -1

model_version = 1

if node == None:
    node_id = gc.createNode("model", "model")["id"]
else:
    parents = gc.getNodeLatestVersions("model")
    model_version = gc.getNodeVersion(max(parents))["tags"]["version"]["value"] + 1
    node_id = node["id"]

tags = {
    "version": {
        "key": "version",
        "value": model_version,
        "type": "integer"
    }
}

model_id = gc.createNodeVersion(node_id, tags=tags, parent_ids=parents)["id"]

# get the latest version of the table info
latest_table_version = gc.getNodeLatestVersions("table_tweets")[0]

# create the lineage
ctm_id = -1
dtm_id = -1
ctm = gc.getLineageEdge("code_to_model")


if ctm == None:
    ctm_id = gc.createLineageEdge("code_to_model", "code_to_model")["id"]
    dtm_id = gc.createLineageEdge("data_to_model", "data_to_model")["id"]
else:
    ctm_id = ctm["id"]
    dtm_id = gc.getLineageEdge("data_to_model")["id"]

gc.createLineageEdgeVersion(ctm_id, latest_git_version, model_id)
gc.createLineageEdgeVersion(dtm_id, latest_table_version, model_id)
