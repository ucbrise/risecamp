#!/usr/bin/env python
import numpy as np

# Define the names of each column in the tweets file
attribute_names = []
attribute_names.append('id')
attribute_names.append('tweet')
attribute_names.append('code')
attribute_names.append('city')
attribute_names.append('country')

# Define the data type of every element in a column
attribute_types = {
    'id': np.int32,
    'tweet': str,
    'place': str,
    'city': str,
    'country': str,
    'code': str
}

# Read the twitter data into a pandas dataframe
params = dict(header=None, names=attribute_names, dtype=attribute_types)

# Select a relevant subset of features
relevant_attributes = ["tweet", "code"]