#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Samvaran Kashyap Rallabandi -  <srallaba@redhat.com>
#
# Topology validator for Ansible based infra provsioning tool linch-pin

from ansible.module_utils.basic import *
import sys
import json
import os
import yaml
import pickledb

DOCUMENTATION = '''
---
version_added: "0.1"
module: pickledb
short_description: Local database to store and retrive outputs
description:
  - This module allows a user to store variables in a pickledb
options:
  path:
    description:
      path to database file which is used as a store
    required: true
  operation:
    description:
      operation to be performed, get/set
    default: set

author: Samvaran Kashyap Rallabandi -
'''

def check_file_path(path):
    if os.path.isdir(path):
        msg = "Directory not supported as a path %s " % (path)
        module.fail_json(msg=msg)

def get_query_response(path, operation,override, key, value=None):
    output = {}
    db = pickledb.load(path, True)
    if operation == "get":
        output['output'] = db.get(key)
        if output['output'] == None:
            msg = "Key Not found in DB"
            module.fail_json(msg=msg)
        output['changed'] = False
        return output
    if operation == "set":
        if (db.get(key) == None):
            output['changed'] = db.set(key, value)
        else:
            if override == False:
                msg = "Key Found in database, Please use override flag"
                module.fail_json(msg=msg)
            if override == True:
                output['changed'] = db.set(key, value)
        return output

def main():
    global module
    argument_spec = dict(
        path                            = dict(required=True),
        operation                       = dict(default="get", choices=['get', 'set']),
        key                             = dict(required=True),
        value                           = dict(required=False),
        override                        = dict(default=False, type='bool'),
        state                           = dict(default='present', choices=['absent', 'present']),
    )
    module = AnsibleModule(argument_spec)
    path = os.path.expanduser(module.params['path'])
    check_file_path(path)
    operation = module.params['operation']
    key = module.params['key']
    override = module.params['override']
    if operation == 'set' and ('value' in module.params):
        value = module.params['value']
        out = get_query_response(path, operation, override, key, value)
        module.exit_json(changed=out['changed'], output=out)
    elif operation == 'get':
        out = get_query_response(path, operation, override, key)
        module.exit_json(changed=out['changed'], output=out)
    else:
        module.fail_json(msg="Value not specified")

main()
