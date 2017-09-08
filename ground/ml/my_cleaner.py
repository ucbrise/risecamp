#!/usr/bin/env python
import pandas as pd
import numpy as np
import HTMLParser
import preprocessor as tweet_preprocessor
html_parser = HTMLParser.HTMLParser()

def clean(df):
    df["tweet"].apply(html_parser.unescape)
    df["tweet"].apply(tweet_preprocessor.tokenize)
