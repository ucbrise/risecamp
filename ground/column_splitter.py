#!/usr/bin/env python
import pandas as pd
import numpy as np
from ground import GroundClient

gc = GroundClient()

SOURCE_FILE = 'data.txt'
DEST_FILE = 'split_data.csv'

# df = pd.read_csv(SOURCE_FILE, header=None)
# df = df[0].apply(lambda x: pd.Series([i for i in x.split()]))
# df.to_csv(path_or_buf=DEST_FILE, header=False, index=False)

node_id = gc.create_node(DEST_FILE, DEST_FILE)['id']
dst_nv_id = gc.create_node_version(node_id, {'tag': {'key': 'tag', 'value': 'you found the tag!', 'type': 'string'}}, [])['id']

src_nv_id = gc.get_node_latest(SOURCE_FILE)[0]

le_key = SOURCE_FILE + '_to_' + DEST_FILE
le_id = gc.create_lineage_edge(le_key, le_key)['id']

git_id = gc.get_node_latest('ground-context/risecamp')[0]
git_sha = gc.get_node_vesion(git_id)['tags']['commit']['value']

json = gc.create_le_version(le_id, src_nv_id, dst_nv_id, {'git_commit': {'key': 'git_commit': 'value': git_sha, 'type': 'string'}})
