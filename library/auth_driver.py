#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Samvaran Kashyap Rallabandi -  <srallaba@redhat.com>
#
# Auth driver  for Ansible based infra provsioning tool, linch-pin
DOCUMENTATION = '''
---
version_added: "0.1"
module: auth_driver
short_description: auth_driver module in ansible
description:
  - This module allows a user to fetch credentials on request and egister it as variable in ansible.

options:
  type:
    description:
      type of credential required
    required: true

author: Samvaran Kashyap Rallabandi -
'''
from ansible.module_utils.basic import *
import datetime
import sys
import json
import os
import shlex
import tempfile
import yaml
from credentials.credentials import get_creds, get_default_creds

def check_file_paths(module, *args):
    for file_path in args:
        if not os.path.exists(file_path):
            module.fail_json(msg= "File not found %s not found" % (file_path))
        if not os.access(file_path, os.R_OK):
            module.fail_json(msg= "File not accesible %s not found" % (file_path))
        if os.path.isdir(file_path):
            module.fail_json(msg= "Recursive directory not supported  %s " % (file_path))

def search_cred(module, cred_type, cred_store, cred_name):
    try:
        cred = get_creds(cred_type, cred_store, cred_name)
        cred = None
        if cred == None:
            cred = get_default_creds(cred_type, cred_store, cred_name) 
        return cred
    except Exception as e:
        #module.fail_json(msg="Auth driver failed to fetch cred_obj:ERROR:"+str(e)) 
        print e 

def main():
    module = AnsibleModule(
    argument_spec={
            'type': {'required': True, 'aliases': ['auth_type']},
            'cred_store': {'required': True, 'aliases': ['credential_store']},
            'cred_name': {'required': True, 'aliases': ['credential_name']},
            'profile': {'required': False, 'aliases': ['profile_name']},
        },
        required_one_of=[],
        supports_check_mode=True
    )
    cred_type = module.params['type']
    cred_store = module.params['cred_store']
    cred_name = module.params['cred_name']
    profile = module.params['profile']
    output = get_cred(cred_type, cred_store, profile)
    changed = True
    module.exit_json(changed=changed, output=output)

from ansible.module_utils.basic import *
main()

"""
#debug statements
import pdb
pdb.set_trace()
print get_creds("aws","/root/linch-pin.work/credential_store","botoconfig")
print get_creds("aws","/root/linch-pin.work/credential_store","botoconfig","another_profile")
print get_creds("openstack","/root/linch-pin.work/credential_store","clouds","devstack")
print get_creds("openstack","/root/linch-pin.work/credential_store","clouds","")
print get_creds("gcloud","/root/linch-pin.work/credential_store","gcloud")
#print search_cred("", "aws", "/root/linch-pin.work/credential_store", "testname")
#print search_cred("", "openstack", "/root/linch-pin.work/credential_store", "testname")
#print search_cred("", "gcloud", "/root/linch-pin.work/credential_store", "testname")
#print search_cred("", "example", "/root/linch-pin.work/credential_store", "testname")
"""
