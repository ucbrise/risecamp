import os
import subprocess

def reset_ground():
    os.chdir("/home/jovyan/ground/resources/scripts/postgres")
    process = subprocess.Popen(["python2.7", "postgres_setup.py", "ground", "ground", "drop"], stdout = subprocess.pipe)
    process.communicate()
    os.chdir("/home/jovyan/risecamp")
