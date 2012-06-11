import os
import subprocess

def commitAll():
    cmd = 'git add *; git commit -a -m "Latest update"'
    pipe = subprocess.Popen(cmd, shell=True, cwd=os.getcwd())
    pipe.wait()

def commitFile(file_name):
    cmd = 'git add %s; git commit -m "Latest update"' % file_name
    pipe = subprocess.Popen(cmd, shell=True, cwd=os.getcwd())
    pipe.wait()

def commit(fn):
    def git(filename):
        new_file = fn(filename)
        commitFile(new_file)
        return new_file
    return git
