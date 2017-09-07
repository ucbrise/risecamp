#!/usr/bin/env python
import os
import subprocess
import pandas as pd
from ml.driver import debug
import pprint

from ground.client import GroundClient

abspath = os.path.dirname(os.path.abspath(__file__))

def __run_proc__(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output

def setup():
    os.chdir(abspath)
    __run_proc__("bash setup.sh")
    os.chdir('../')

def display_data():
    os.chdir(abspath)
    __run_proc__("make training_tweets.csv")
    df = pd.read_csv("training_tweets.csv", names=["id", "tweet", "code", "city", "country"])
    __run_proc__("make clean")
    os.chdir('../')
    return df

def show_model_version():
    gc = GroundClient()
    pp = pprint.PrettyPrinter(indent=4)

    if gc.getNode("model") == None:
        print("No model trained yet!")

    pp.pprint(gc.getNodeVersion(gc.getNodeLatestVersions("model")[0]))

def show_all_model_versions():
    gc = GroundClient()
    pp = pprint.PrettyPrinter(indent=4)

    if gc.getNode("model") == None:
        print("No model trained yet!")

    history = gc.getNodeHistory("model")

    print(history)

    prev_parent = 0
    while history:
        child = history[str(prev_parent)]
        del history[str(prev_parent)]

        pp.pprint(gc.getNodeVersion(child))
        prev_parent = child

def show_model_dependencies(version=-1):
    gc = GroundClient()
    pp = pprint.PrettyPrinter(indent=4)

    if gc.getNode("model") == None:
        print("No model trained yet!")

    if version < 0:
        version = gc.getNodeLatestVersions("model")[0]

    model = gc.getNodeVersion(version)

    print("MODEL VERSION: " + str(model["tags"]["version"]["value"]) + " (ground id "+ str(version) + ")")

    deps = [gc.getNodeVersion(gc.getLineageEdgeVersion(y)['toRichVersionId']) for y in gc.getNodeVersionAdjacentLineage(version)]

    for dep in deps:
        if "commit" in dep["tags"]:
            print("\tCODE: " + dep["tags"]["commit"]["value"])
        else:
            print("\tDATA: ground version " + str(dep["id"]) + "\n\t\tschema: " + ", ".join(dep["tags"].keys()))


def _get_data_schema(version=-1):
    gc = GroundClient()

    if version < 0:
        version = gc.getNodeLatestVersion("table_tweets")[0]

    data_schema = gc.getNodeVersion(version)

    return data_schema["tags"]

def show_data_schema(version=-1):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(_get_data_schema(version))

def diff_data_schemas(old_version, new_version):
    if old_version > new_version:
        temp = new_version
        new_version = old_version
        old_version = temp

    old_schema = _get_data_schema(old_version)
    new_schema = _get_data_schema(new_version)

    deleted = []
    changed = []

    for key in old_schema.keys():
        if key not in new_schema:
            deleted.append(key)
        else:
            del new_schema[key]["id"]
            del old_schema[key]["id"]
            if new_schema[key] != old_schema[key]:
                changed.append(key)

    print("REMOVED: " + ", ".join(deleted))

    print("CHANGED: \n")
    for k in changed:
        print("\t" + k + " in old: " + str(old_schema[k]))
        print()
        print("\t" + k + " in new: " + str(new_schema[k]))
        print()
        print()
        print()

def test_model():
    os.chdir(abspath)
    __run_proc__("make clean")
    output = __run_proc__("make test -j")
    __run_proc__("make clean")
    os.chdir('../')
    return output
