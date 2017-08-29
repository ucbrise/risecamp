#!/usr/bin/env python
import pandas as pd
import numpy as np

def clean(df):
    df["code"] = df["country"]