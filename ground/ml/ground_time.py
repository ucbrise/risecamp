import subprocess

def fast_forward():
    process = subprocess.Popen(["bash", "break.sh"], cwd="ml/")
    process.communicate()
