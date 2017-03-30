import os
import sys
import inspect
import ansible
import pprint
from tabulate import tabulate
from ansible import utils
import jsonschema as jsch
from collections import namedtuple
from ansible import utils
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from callbacks import PlaybookCallback
from invoke_playbooks import invoke_linchpin
from linchpin.cli.utils import search_path
from utils import get_file, list_files, parse_yaml
from github import GitHub


class LinchpinAPI:

    def __init__(self):
        base_path = os.path.dirname(__file__).split("/")[0:-2]
        self.base_path = "/{}/linchpin/".format('/'.join(base_path))
        self.excludes = set(["topology_upstream",
                             "layout_upstream",
                             "post_actions"])

    def get_config_path(self):
        try:
            cwd = os.getcwd()
            config_files = [
                            cwd+"/linchpin_config.yml",
                            cwd+"/linch-pin/linchpin_config.yml", #for jenkins
                            "~/.linchpin_config.yml",
                            self.base_path+"/linchpin_config.yml",
                            "/etc/linchpin_config.yml"]
            for p in sys.path:
                config_files.extend(['{}/linchpin/linchpin_config.yml'.format(p)])

            for c_file in config_files:
#                print(c_file)
                if os.path.isfile(c_file):
#                    print("debug:: File found returning ::")
#                    print(c_file)
                    return c_file
        except Exception as e:
            print(e)

    def get_config(self):
        config_path = self.get_config_path()
        config = parse_yaml(config_path)
        return config

    def get_evars(self, pf):
        """ creates a group of extra vars on basis on linchpin file dict """
        e_vars = []
        for group in pf:
            if not (group in ["post_actions", 
                              "topology_upstream",
                              "layout_upstream"]):
                topology = pf[group].get("topology")
                layout = pf[group].get("layout")
                e_var_grp = {}
                e_var_grp["topology"] = search_path(topology, os.getcwd())
                e_var_grp["layout"] = search_path(layout, os.getcwd())
                if None in e_var_grp.values():
                    raise Exception("Topology or Layout mentioned \
                                     in pf file not found . \
                                     Please check your pf file.")
                e_vars.append(e_var_grp)
        return e_vars

    def lp_list(self, config, topos=False, layouts=False):
        """ list module of linchpin  """
        if topos and layouts:
            t_files = list_files(config.clipath+"/ex_topo")
            l_files = list_files(config.clipath+"/inventory_layouts")
            return (t_files, l_files)
        if topos:
            t_files = list_files(config.clipath+"/ex_topo")
            return t_files
        if layouts:
            l_files = list_files(config.clipath+"/inventory_layouts")
            return l_files

    def lp_topo_list(self, upstream=None):
        """
        search_order : list topologies from upstream if mentioned
                       list topologies from current folder
        """
        if upstream is None:
            t_files = list_files(self.base_path + "/ex_topo")
            return t_files
        else:
            print "getting from upstream"
            g = GitHub(upstream)
            t_files = []
            files = g.list_files("ex_topo")
            return files

    def lp_topo_get(self, topo, upstream=None):
        """
        search_order : get topologies from upstream if mentioned
                       get topologies from core package
        # need to add checks for ./topologies
        """
        if upstream is None:
            get_file(self.base_path + "/ex_topo/" + topo, "./topologies/")
        else:
            g = GitHub(upstream)
            files = g.list_files("ex_topo")
            link = filter(lambda link: link['name'] == topo, files)
            link = link[0]["download_url"]
            get_file(link, "./topologies", True)
            return link

    def lp_layout_list(self, upstream=None):
        """
        search_order : list layouts from upstream if mentioned
                       list layouts from core package
        """
        if upstream is None:
            l_files = list_files(self.base_path + "/inventory_layouts")
            return l_files
        else:
            g = GitHub(upstream)
            l_files = []
            files = g.list_files("inventory_layouts")
            return files

    def lp_layout_get(self, layout, upstream=None):
        """
        search_order : get layouts from upstream if mentioned
                       get layouts from core package
        """
        if upstream is None:
            get_file(self.base_path + "/inventory_layouts/" + layout,
                     "./layouts/")
        else:
            g = GitHub(upstream)
            files = g.list_files("inventory_layouts")
            link = filter(lambda link: link['name'] == layout, files)
            link = link[0]["download_url"]
            get_file(link, "./layouts", True)
            return link

    def lp_drop(self, config, pf):
        """ drop module of linchpin cli : find implementation in cli.py
        inventory_outputs paths"""
        init_dir = os.getcwd()
        pfs = list_by_ext(init_dir, "PinFile")
        if len(pfs) == 0:
            display("ERROR:001")
        if len(pfs) > 1:
            display("ERROR:002")
        pf = pfs[0]
        pf = parse_yaml(pf)
        e_vars = {}
        e_vars['linchpin_config'] = self.get_config_path()
        e_vars['outputfolder_path'] = self.context.workspace+"/outputs"
        e_vars['inventory_outputs_path'] = self.context.workspace+"/inventories"
        e_vars['keystore_path'] = self.context.workspace+"/keystore"
        e_vars['state'] = "present"
        # checks wether the targets are valid or not
        if set(targets) == set(pf.keys()).intersection(targets) and len(targets) > 0:
            for target in targets:
                topology = pf[target]['topology']
                topology_registry = pf.get("topology_registry", None)
                e_vars['topology'] = self.find_topology(pf[target]["topology"],
                                                        topology_registry)
                if pf[target].has_key("layout"):
                    e_vars['inventory_layout_file'] = self.context.workspace+"/layouts/"+pf[target]["layout"]
                output = invoke_linchpin(self.base_path,
                                         e_vars,
                                         "PROVISION",
                                         console=True)

        elif len(targets) == 0:
            for target in set(pf.keys()).difference(self.excludes):
                topology = pf[target]['topology']
                topology_registry = pf.get("topology_registry", None)
                e_vars['topology'] = self.find_topology(pf[target]["topology"],
                                                        topology_registry)
                if pf[target].has_key("layout"):
                    e_vars['inventory_layout_file'] = self.context.workspace+"/layouts/"+pf[target]["layout"]
                output = invoke_linchpin(self.base_path, e_vars, "PROVISION",
                                         console=True)
        else:
            raise  KeyError("One or more Invalid targets found")

    def lp_rise(self, pf, target):
        """ rise module of linchpin cli find implementation in cli.py"""
        init_dir = os.getcwd()
        pfs = list_by_ext(init_dir, "PinFile")
        pf = pfs[0]
        pf = parse_yaml(pf)
        e_vars = {}
        e_vars['linchpin_config'] = self.get_config_path()
        e_vars['inventory_outputs_path'] = self.context.workspace + "/inventories"
        e_vars['keystore_path'] = self.context.workspace+"/keystore"
        e_vars['state'] = "absent"
        # checks wether the targets are valid or not
        if set(targets) == set(pf.keys()).intersection(targets) and len(targets) > 0:
            for target in targets:
                topology = pf[target]['topology']
                topology_registry = pf.get("topology_registry", None)
                e_vars['topology'] = self.find_topology(pf[target]["topology"],
                                                        topology_registry)
                output = invoke_linchpin(self.base_path,
                                         e_vars,
                                         "TEARDOWN",
                                         console=True)

        elif len(targets) == 0:
            for target in set(pf.keys()).difference(self.excludes):
                e_vars['topology'] = self.find_topology(pf[target]["topology"],
                                                        pf)
                topology = pf[target]["topology"].strip(".yml").strip(".yaml")
                output_file = ( self.context.workspace + "/outputs/" + 
                                topology + ".output" )
                e_vars['topology_output_file'] = output_file
                output = invoke_linchpin(self.base_path,
                                         e_vars,
                                         "TEARDOWN",
                                         console=True)
        else:
            raise  KeyError("One or more Invalid targets found")


    def lp_validate(self, topo, layout=None, pf=None):
        """ validate module of linchpin cli :
        currenly validates only topologies,
        need to implement pf, layouts too"""
        e_vars = {}
        e_vars["schema"] = self.base_path + "/schemas/schema_v3.json"
        e_vars["data"] = topo
        result = invoke_linchpin(self.base_path, e_vars,
                                 "SCHEMA_CHECK", console=True)
        return result

    def lp_invgen(self, topoout, layout, invout, invtype):
        """ invgen module of linchpin cli """
        e_vars = {}
        e_vars['linchpin_config'] = self.get_config_path()
        e_vars['output'] = os.path.abspath(topoout)
        e_vars['layout'] = os.path.abspath(layout)
        e_vars['inventory_type'] = invtype
        e_vars['inventory_output'] = invout
        result = invoke_linchpin(self.base_path,
                                 e_vars,
                                 "INVGEN",
                                 console=True)

    def lp_test(self, topo, layout, pf):
        """ test module of linchpin.api"""
        e_vars = {}
        e_vars['data'] = topo
        e_vars['schema'] = self.base_path + "/schemas/schema_v3.json"
        result = invoke_linchpin(self.base_path, e_vars, "TEST", console=True)
        return result
