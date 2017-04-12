import yaml
import json
import ansible
from ansible import utils
from collections import namedtuple
from ansible import utils
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase

class AnsibleActionManager:
    def __init__(self, name, action_data, target_data, *args, **kwargs):
        self.name = name
        self.action_data = action_data
        self.target_data = target_data
        self.args = args
        self.kwargs = kwargs

    def validate():
        pass

    def load(self):
        print("Load module of Ansible Action Manager ")
        print("Action data "+str(self.action_data))
        print("Target data "+str(self.target_data))
        self.loader = DataLoader()
        self.variable_manager = VariableManager()
        self.passwords = {}
        if self.target_data.has_key("inventory"):
            self.inventory = Inventory(loader=self.loader,
                                       variable_manager=self.variable_manager,
                                       host_list=self.target_data["inventory"])
        else:
            self.inventory = Inventory(loader=self.loader,
                                       variable_manager=self.variable_manager,
                                       host_list=["localhost"])
        Options = namedtuple('Options', ['listtags',
                                         'listtasks',
                                         'listhosts',
                                         'syntax',
                                         'connection',
                                         'module_path',
                                         'forks',
                                         'remote_user',
                                         'private_key_file',
                                         'ssh_common_args',
                                         'ssh_extra_args',
                                         'sftp_extra_args',
                                         'scp_extra_args',
                                         'become',
                                         'become_method',
                                         'become_user',
                                         'verbosity',
                                         'check'])
        utils.VERBOSITY = 4
        self.options = Options(listtags=False,
                          listtasks=False,
                          listhosts=False,
                          syntax=False,
                          connection='ssh',
                          module_path="",
                          forks=100,
                          remote_user='root',
                          private_key_file=None,
                          ssh_common_args=None,
                          ssh_extra_args=None,
                          sftp_extra_args=None,
                          scp_extra_args=None,
                          become=True,
                          become_method="sudo",
                          become_user='root',
                          verbosity=utils.VERBOSITY,
                          check=False)


    def get_ansible_runner(self, playbook_path, extra_vars):
        self.variable_manager.extra_vars = extra_vars
        # though verbosity through api doesnot work
        pbex = PlaybookExecutor(playbooks=[playbook_path],
                                inventory=self.inventory,
                                variable_manager=self.variable_manager,
                                loader=self.loader,
                                options=self.options,
                                passwords=self.passwords)
        return pbex


    def execute(self):
        print("Execute module of Ansible Action Manager")
        self.load()
        extra_vars = {}
        for action in self.action_data["actions"]:
            print("action is")
            print(action)
            if self.action_data.get("path", None):
                path = self.action_data["path"]
                playbook = path+"/"+action.get("playbook")
                if action.has_key("vars"):
                    var_file = path+"/"+action.get("vars")
                    ext = var_file.split(".")[-1]
                    extra_vars = open(var_file,"r").read()
                    if ("yaml" in ext) or ("yml" in ext):
                        extra_vars = yaml.load(extra_vars)
                    else:
                        extra_vars = json.loads(extra_vars)
            else:
                playbook = action.get("playbook")
                var_file = action.get("vars")
                ext = var_file.split(".")[-1]
                extra_vars = open(var_file,"r").read()
                if ("yaml" in ext) or ("yml" in ext):
                    extra_vars = yaml.load(extra_vars)
                else:
                    extra_vars = json.loads(extra_vars)
            e_vars = action.get("extra_vars", {})
            extra_vars.update(e_vars)
            print extra_vars
            pbex = self.get_ansible_runner(playbook, extra_vars)
            results = pbex.run()

