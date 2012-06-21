import os
import subprocess

from threading import Lock

GIT_LOCK = Lock()

def commitAll(path=os.getcwd(), msg="Latest update"):
    with GIT_LOCK:
        cmd = 'git add *; git commit -a -m "%s"' % msg
        pipe = subprocess.Popen(cmd, shell=True, cwd=path)
        pipe.wait()

def commitFile(file_name, path=os.getcwd(), msg="Latest update"):
    with GIT_LOCK:
        cmd = 'git add %s; git commit -m "%s"' % (file_name, path)
        pipe = subprocess.Popen(cmd, shell=True, cwd=path)
        pipe.wait()

def commit(fn):
    def git(filename):
        new_file = fn(filename)
        commitFile(new_file)
        return new_file
    return git
