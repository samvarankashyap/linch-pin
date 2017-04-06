#!/usr/bin/env python
import sys
print sys.argv
print("Hello world from python")
import json
print sys.argv[1]
print type(sys.argv[1])
h = json.loads(sys.argv[1])
print h
print type(h)
print sys.argv[1]
