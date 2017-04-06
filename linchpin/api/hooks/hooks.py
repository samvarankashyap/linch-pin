import os
import glob
from os import listdir
from os.path import isfile, join
import json
import sys
import subprocess
from subprocess import PIPE, Popen
from threading  import Thread


HOOKS_LIB="./hooks_folder/"


def execute(command):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE,bufsize=1)
    lines_iterator = iter(popen.stdout.readline, b"")
    while popen.poll() is None:
        for line in lines_iterator:
            nline = line.rstrip()
            print(nline)
            sys.stdout.flush()

def get_hook(name):
    abs_path = os.path.abspath(HOOKS_LIB)
    onlyfiles = glob.glob(abs_path+"/*")
    for file_name in onlyfiles:
        if name == file_name.split("/")[-1].split(".")[0]:
            return file_name


def run_hook(name, args, meta):
    hook = get_hook(name)
    command = [hook, args, meta]
    execute(command)

#def main():
#    test_dict = { "hello": "world"}
#    run_hook("shell_hook","{'dasdsa': 'hel'}", "{'topology_path':'/testpath/test.txt'}")
#    run_hook("python_hook",json.dumps(test_dict), "{'topology_path':'/testpath/test.txt'}")
#
#main()
