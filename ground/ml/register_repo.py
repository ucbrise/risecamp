#!/usr/bin/env python

from ground.client import GroundClient
import os
import subprocess

commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()

gc = GroundClient()

node_id = gc.createNode("ml_repo", "ml_repo")["id"]

tags = {
    "commit": {
        "key": "commit",
        "value": commit,
        "type": "string"
    },
    "branch": {
        "key": "branch",
        "value": "master",
        "type": "string"
    }
}

nv = gc.createNodeVersion(node_id, tags=tags)
print(nv)
