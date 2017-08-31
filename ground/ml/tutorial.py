#!/usr/bin/env python
import os
import subprocess
import pandas as pd
from ml.driver import debug

abspath = os.path.dirname(os.path.abspath(__file__))
__toggle__ = True

def __run_proc__(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output

def setup():
    os.chdir(abspath)
    __run_proc__("sudo bash setup.sh")
    os.chdir('../')

def show_me_data():
    os.chdir(abspath)
    __run_proc__("sudo make training_tweets.csv")
    df = pd.read_csv("training_tweets.csv", names=["id", "tweet", "code", "city", "country"])
    __run_proc__("sudo make clean")
    os.chdir('../')
    return df

def get_ground_metadata():
    return debug()

def test_model():
    global __toggle__
    os.chdir(abspath)
    __run_proc__("sudo make clean")
    output = __run_proc__("sudo make test -j")
    if __toggle__:
        __run_proc__("sudo bash break.sh")
        __toggle__ = not __toggle__
    __run_proc__("sudo make clean")
    os.chdir('../')
    return output
