#!/usr/bin/env python
import pandas as pd
import numpy as np
df = pd.read_csv('codes.txt', header=None)
df = df[0].apply(lambda x: pd.Series([i for i in x.split()]))
df.to_csv(path_or_buf='codes_3_col.csv', header=False, index=False)