import os
import subprocess

def commitAll():
    cmd = 'git add *; git commit -a -m "Latest update"'
    pipe = subprocess.Popen(cmd, shell=True, cwd=os.getcwd())
    pipe.wait()

