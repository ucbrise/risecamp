#!/usr/bin/env python3

import pandas as pd
import random

df = pd.read_csv('imitation_data.csv')
new_df = pd.DataFrame(columns=df.columns)

ni = 0

for i in range(len(df)):
    new_df.loc[ni] = df.loc[i]
    ni += 1

    if random.random() < 0.6:
        new_df.loc[ni] = df.loc[i]
        new_df.at[ni, 'user'] = 'ion'
        new_df.at[ni, 'label'] = random.choice(['up', 'down', 'stop'])

        ni += 1

new_df.to_csv('dirty_imitation.csv')
