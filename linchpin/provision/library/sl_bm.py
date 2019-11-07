#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: sl_bm
short_description: create or cancel a virtual instance in SoftLayer
description:
  - Creates or cancels SoftLayer instances.
  - When created, optionally waits for it to be 'running'.
version_added: "2.1"
options:
  instance_id:
    description:
      - Instance Id of the virtual instance to perform action option.
  hostname:
    description:
      - Hostname to be provided to a virtual instance.
  domain:
    description:
      - Domain name to be provided to a virtual instance.
  datacenter:
    description:
      - Datacenter for the virtual instance to be deployed.
  tags:
    description:
      - Tag or list of tags to be provided to a virtual instance.
  hourly:
    description:
      - Flag to determine if the instance should be hourly billed.
    type: bool
    default: 'yes'
  private:
    description:
      - Flag to determine if the instance should be private only.
    type: bool
    default: 'no'
  dedicated:
    description:
      - Flag to determine if the instance should be deployed in dedicated space.
    type: bool
    default: 'no'
  local_disk:
    description:
      - Flag to determine if local disk should be used for the new instance.
    type: bool
    default: 'yes'
  cpus:
    description:
      - Count of cpus to be assigned to new virtual instance.
    required: true
  memory:
    description:
      - Amount of memory to be assigned to new virtual instance.
    required: true
  flavor:
    description:
      - Specify which SoftLayer flavor template to use instead of cpus and memory.
    version_added: "2.10"
  disks:
    description:
      - List of disk sizes to be assigned to new virtual instance.
    required: true
    default: [ 25 ]
  os_code:
    description:
      - OS Code to be used for new virtual instance.
  image_id:
    description:
      - Image Template to be used for new virtual instance.
  nic_speed:
    description:
      - NIC Speed to be assigned to new virtual instance.
    default: 10
  public_vlan:
    description:
      - VLAN by its Id to be assigned to the public NIC.
  private_vlan:
    description:
      - VLAN by its Id to be assigned to the private NIC.
  ssh_keys:
    description:
      - List of ssh keys by their Id to be assigned to a virtual instance.
  post_uri:
    description:
      - URL of a post provisioning script to be loaded and executed on virtual instance.
  state:
    description:
      - Create, or cancel a virtual instance.
      - Specify C(present) for create, C(absent) to cancel.
    choices: [ absent, present ]
    default: present
  wait:
    description:
      - Flag used to wait for active status before returning.
    type: bool
    default: 'yes'
  wait_time:
    description:
      - Time in seconds before wait returns.
    default: 600
requirements:
    - python >= 2.6
    - softlayer >= 4.1.1
author:
- Matt Colton (@mcltn)
'''

EXAMPLES = '''
- name: Build instance
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Build instance request
    sl_vm:
      hostname: instance-1
      domain: anydomain.com
      datacenter: dal09
      tags: ansible-module-test
      hourly: yes
      private: no
      dedicated: no
      local_disk: yes
      cpus: 1
      memory: 1024
      disks: [25]
      os_code: UBUNTU_LATEST
      wait: no

- name: Build additional instances
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Build instances request
    sl_vm:
      hostname: "{{ item.hostname }}"
      domain: "{{ item.domain }}"
      datacenter: "{{ item.datacenter }}"
      tags: "{{ item.tags }}"
      hourly: "{{ item.hourly }}"
      private: "{{ item.private }}"
      dedicated: "{{ item.dedicated }}"
      local_disk: "{{ item.local_disk }}"
      cpus: "{{ item.cpus }}"
      memory: "{{ item.memory }}"
      disks: "{{ item.disks }}"
      os_code: "{{ item.os_code }}"
      ssh_keys: "{{ item.ssh_keys }}"
      wait: "{{ item.wait }}"
    with_items:
      - hostname: instance-2
        domain: anydomain.com
        datacenter: dal09
        tags:
          - ansible-module-test
          - ansible-module-test-slaves
        hourly: yes
        private: no
        dedicated: no
        local_disk: yes
        cpus: 1
        memory: 1024
        disks:
          - 25
          - 100
        os_code: UBUNTU_LATEST
        ssh_keys: []
        wait: True
      - hostname: instance-3
        domain: anydomain.com
        datacenter: dal09
        tags:
          - ansible-module-test
          - ansible-module-test-slaves
        hourly: yes
        private: no
        dedicated: no
        local_disk: yes
        cpus: 1
        memory: 1024
        disks:
          - 25
          - 100
        os_code: UBUNTU_LATEST
        ssh_keys: []
        wait: yes

- name: Cancel instances
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Cancel by tag
    sl_vm:
      state: absent
      tags: ansible-module-test
'''

# TODO: Disabled RETURN as it is breaking the build for docs. Needs to be fixed.
RETURN = '''# '''

import json
import time

try:
    import SoftLayer
    from SoftLayer import HardwareManager

    HAS_SL = True
except ImportError:
    HAS_SL = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import string_types


# TODO: get this info from API
STATES = ['present', 'absent']
DATACENTERS = ['ams01', 'ams03', 'che01', 'dal01', 'dal05', 'dal06', 'dal09', 'dal10', 'dal12', 'dal13', 'fra02',
               'fra04', 'fra05', 'hkg02', 'hou02', 'lon02', 'lon04', 'lon06', 'mel01', 'mex01', 'mil01', 'mon01',
               'osl01', 'par01', 'sao01', 'sea01', 'seo01', 'sjc01', 'sjc03', 'sjc04', 'sng01', 'syd01', 'syd04',
               'tok02', 'tor01', 'wdc01', 'wdc04', 'wdc06', 'wdc07']
CPU_SIZES = [1, 2, 4, 8, 16, 32, 56]
MEMORY_SIZES = [1024, 2048, 4096, 6144, 8192, 12288, 16384, 32768, 49152, 65536, 131072, 247808]
INITIALDISK_SIZES = [25, 100]
LOCALDISK_SIZES = [25, 100, 150, 200, 300]
SANDISK_SIZES = [10, 20, 25, 30, 40, 50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 750, 1000, 1500, 2000]
NIC_SPEEDS = [10, 100, 1000]


def softlayer_client_from_module(module,  min_version='0.12.0'):
    from distutils.version import StrictVersion
    global bmManager
    try:
        # Due to the name shadowing we should import other way
        import importlib
        sdk = importlib.import_module('SoftLayer')
    except ImportError:
        module.fail_json(msg='softlayer is required for this module')

    if min_version:
        min_version = max(StrictVersion('0.12.0'), StrictVersion(min_version))
    else:
        min_version = StrictVersion('0.12.0')

    if StrictVersion(sdk.__version__.strip("v")) < min_version:
        module.fail_json(
            msg="To utilize this module, the installed version of "
                "the softlayer library MUST be >={min_version}.".format(
                    min_version=min_version))
    auth = module.params.pop('auth', None)
    if auth and isinstance(auth, dict):
        for param in ('username', 'api_key'):
            if param not in auth:
                module.fail_json(
                    msg="auth parameter {param} not found in auth"
                    "dictionary passed to module".format(
                    param=param))
        client = SoftLayer.create_client_from_env(
                        username=auth.get('username'),
                        api_key=auth.get('api_key'),
                        timeout=auth.get('timeout', 240))
        bmManager = HardwareManager(client)
        return bmManager
    else:
        client = SoftLayer.create_client_from_env()
        bmManager = HardwareManager(client)
        return bmManager


def create_hardware_instance(module):

    instances = bmManager.list_hardware(
        hostname=module.params.get('hostname'),
        domain=module.params.get('domain'),
        datacenter=module.params.get('datacenter')
    )



    if instances:
        # return data of instances if they exists
        return False, instances


    instance = bmManager.place_order(
        hostname=module.params.get('hostname'),
        domain=module.params.get('domain'),
        size=module.params.get('size'),
        location=module.params.get('location'),
        os=module.params.get('os'),
        port_speed=module.params.get('port_speed'),
        hourly=module.params.get('hourly'),
        ssh_keys=module.params.get('ssh_keys'),
        post_uri=module.params.get('post_uri'),
        no_public=module.params.get('no_public'),
        extras=module.params.get('extras')
    )

    if instance is not None:
        module.exit_json(changed=True, instance=instance)
        return True, instance
    else:
        return False, None


def wait_for_instance(module, id):
    instance = None
    completed = False
    wait_timeout = time.time() + module.params.get('wait_time')
    while not completed and wait_timeout > time.time():
        try:
            completed = bmManager.wait_for_ready(id, 10, 2)
            if completed:
                instance = bmManager.get_instance(id)
        except Exception:
            completed = False

    return completed, instance


def cancel_hardware(module):
    canceled = True
    if module.params.get('hardware_id') is None and (module.params.get('tags') or module.params.get('hostname') or module.params.get('domain')):
        tags = module.params.get('tags')
        if isinstance(tags, string_types):
            tags = tags.split(",")

        instances = bmManager.list_hardware(tags=tags, hostname=module.params.get('hostname'), domain=module.params.get('domain'))
        
        for instance in instances:
            try:
                if module.params.get('reason') or module.params.get('comment') or module.params.get('immediate'):
                    bmManager.cancel_hardware(instance['id'],
                                              reason=module.params.get('reason'),
                                              comment=module.params.get('comment'),
                                              immediate=module.params.get('immediate'))
                else:
                    bmManager.cancel_hardware(instance['id'])
            except Exception as e:
                #module.exit_json(changed=False, msg=str(e))
                changed = False
    elif module.params.get('hardware_id') and module.params.get('hardware_id') != 0:
        try:
            #module.exit_json(changed=False, msg="reached")
            bmManager.cancel_hardware(module.params.get('hardware_id'))
        except Exception as e:
            module.exit_json(changed=False, msg=str(e))
            canceled = False
    else:
        return False, None

    return canceled, None


def main():
    """
      - name: Build instance request
    sl_vm:
      auth:
        username: DSW2001944
        api_key: 8a29bbe9fb49cd8f31873f988989abd018052892ef67cf8e6e8c6c60fa532649
      size: S1270V6_16GB_1X2TB_SATA_NORAID
      hostname: samvaranlinchpin
      domain: anydomain.com
      hourly: yes
      location: "sjc03"
      os: "OS_CENTOS_7_X_64_BIT"
      port_speed: 100
      ssh_keys:
        - 1617672
      hourly: True
      no_public: False
      wait: yes
      state: absent
    register: sl_bm_var

    size (string) – server size name or presetId
    hostname (string) – server hostname
    domain (string) – server domain name
    location (string) – location (datacenter) name
    os (string) – operating system name
    port_speed (int) – Port speed in Mbps
    ssh_keys (list) – list of ssh key ids
    post_uri (string) – The URI of the post-install script to run after reload
    hourly (boolean) – True if using hourly pricing (default). False for monthly.
    no_public (boolean) – True if this server should only have private interfaces
    extras (list) – List of extra feature names

    """

    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(default=None, type='dict', no_log=False),
            hardware_id=dict(type='int'),
            reason=dict(type='str', default='Uneeded'),
            comment=dict(type='str', default='Uneeded'),
            immediate=dict(type='bool', default=False),
            size=dict(type='str'),
            hostname=dict(type='str'),
            domain=dict(type='str'),
            location=dict(type='str', choices=DATACENTERS),
            hourly=dict(type='bool', default=True),
            os=dict(type='str'),
            port_speed=dict(type='int', choices=NIC_SPEEDS),
            ssh_keys=dict(type='list', default=[]),
            post_uri=dict(type='str'),
            no_public=dict(type='bool', default=True),
            extras=dict(type='list', default=[]),
            state=dict(type='str', default='present', choices=STATES),
            wait=dict(type='bool', default=True),
            wait_time=dict(type='int', default=600),
        )
    )

    if not HAS_SL:
        module.fail_json(msg='softlayer python library required for this module')
    softlayer_client_from_module(module)
    if module.params.get('state') == 'absent':
        (changed, instance) = cancel_hardware(module)

    elif module.params.get('state') == 'present':
        (changed, instance) = create_hardware_instance(module)
        if module.params.get('wait') is True and instance and (changed):
            (changed, instance) = wait_for_instance(module, instance['id'])

    module.exit_json(changed=changed, instance=json.loads(json.dumps(instance, default=lambda o: o.__dict__)))


if __name__ == '__main__':
    main()
