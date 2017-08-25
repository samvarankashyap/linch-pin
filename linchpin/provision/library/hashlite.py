#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Clint Savage- @herlo <herlo@redhat.com>
#
# Provision a dummy server. Useful for testing the linchpin api provisioner
# without using actual resources.

import os
import re
import json
import tempfile

from ansible.module_utils.basic import AnsibleModule

# ---- Documentation Start ----------------#
DOCUMENTATION = '''
---
version_added: "0.1"
module: hashlite
short_description: Simple database store implemented in json
description:
  - This module allows a user to store and retrive values.
options:
  file_path:
    description:
      File path where the database is stored.
    required: true
  operation:
    description:
      Operations performed on the database
    required: true
  key:
    description:
    required: false
    default: None
  value:
    description:
    required: false
    default: None
  subkey:
    description:
    required: false
    default: None
  force:
    description:
    required: false
    default: None

requirements: []
author: Samvaran Kashyap Rallabandi - @samvarankashyap
'''

EXAMPLES = '''
'''
from linchpin.rundb.drivers import hashlite

def main():

    module = AnsibleModule(
        argument_spec=dict(
            file_path=dict(type='str', required=True),
            operation=dict(choices=['set',
                                    'get',
                                    'listcreate',
                                    'listpop',
                                    'listpush',
                                    'listreset',
                                    'emptydb',
                                    'delete',
                                    'getfirst',
                                    'dictcreate'],
                            default='get'),
            key=dict(type='str', default=None),
            value=dict(default=None),
            subkey=dict(type='str', default=None),
            force=dict(type='str', default=False),
            datatype=dict(type='str', default="string", choices=["string","json"]),
        ),
    )
    operation = module.params['operation']
    key = module.params['key']
    subkey = module.params['subkey']
    value = module.params['value']
    datatype = module.params['datatype']
    if datatype == "json":
        value = json.loads(value)
    file_path = os.path.expanduser(module.params['file_path'])
    if operation in ['set', 'listcreate', 'listpop','listpush','listreset','delete', 'dictcreate']:
        if operation is None:
            msg = "Module operation {0} requires parameter key ".format(operation)
            module.fail_json(msg=msg)

    try:
        db = hashlite.Hashlite(file_path)
        if operation == "set":
            output = db.set(key=key, value=value, subkey=subkey)
        elif operation == "get":
            output = db.get(key=key, subkey=subkey)
        elif operation == "listcreate":
            output = db.listcreate(key=key, subkey=subkey)
        elif operation == "dictcreate":
            output = db.dictcreate(key=key, subkey=subkey)
        elif operation == "listpop":
            output = db.listpop(key=key, subkey=subkey)
        elif operation == "listpush":
            output = db.listpush(key=key, value=value, subkey=subkey)
        elif operation == "listreset":
            output = db.listreset(key=key, subkey=subkey)
        elif operation == "delete":
            output = db.delete(key=key, subkey=subkey)
        elif operation == "getfirst":
            output = db.getfirst(key=key,subkey=subkey)
        else:
            module.fail_json(msg="Invalid Operation")
        module.exit_json(output=output, changed=output)
    except Exception as e:
        module.fail_json(msg=str(e))

# ---- Import Ansible Utilities (Ansible Framework) -------------------#
main()
