import os
import subprocess

from threading import Lock

GIT_LOCK = Lock()

def commit_all(path=os.getcwd(), msg="Latest update"):
    with GIT_LOCK:
        cmd = 'git add *; git commit -a -m "%s"' % msg
        pipe = subprocess.Popen(cmd, shell=True, cwd=path)
        pipe.wait()

def commit_file(file_name, path=os.getcwd(), msg="Latest update"):
    with GIT_LOCK:
        cmd = 'git add %s; git commit -m "%s"' % (file_name, path)
        pipe = subprocess.Popen(cmd, shell=True, cwd=path)
        pipe.wait()

def commit(func):
    def git(filename):
        new_file = func(filename)
        commit_file(new_file)
        return new_file
    return git
