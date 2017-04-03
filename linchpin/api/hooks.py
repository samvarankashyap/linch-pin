import os
import glob
HOOKS_LIB="./hooks_folder/"
from os import listdir
from os.path import isfile, join

import sys
import subprocess
from subprocess import PIPE, Popen
from threading  import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x


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


def run_hook(name, topology_path, output_path, args):
    hook = get_hook(name)
    command = [hook, topology_path, output_path, args]
    execute(command)

def main():
    print get_hook("python_hook")
    abs_path = os.path.abspath(HOOKS_LIB)
    path = get_hook("python_hook")
    execute(path)
    path = get_hook("ruby_hook")
    execute(path)
    path = get_hook("shell_hook")
    execute(path)
    run_hook("shell_hook","sadas","adsdsa","{ 'dasdsa' : 'hel'}")

main()
