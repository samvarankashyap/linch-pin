#proxy pattern implementation
import pprint
from action_managers import ACTION_MANAGERS


class ActionManager:
    def __init__(self, name, *args, **kwargs):
        self.__implementation = self.__get_implementation(name)(name, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.__implementation, name)

    def __get_implementation(self, class_name):
        action_class = ACTION_MANAGERS.get(class_name, None)
        if action_class == None:
            raise Exception("Action Class %s not found " % (class_name))
        return action_class

class LinchpinHooks(object):
    def __init__(self, api):
        self.api = api
        self.api.bind_to_state(self.run_hooks)

    def run_hooks(self, state, is_global=False):
        print("State change triggered in linchpin api")
        print("Observed State in LinchpinHooks :: "+str(state))
        print("Observer target_data passed")
        print(self.api.current_target_data)
        hooks_data = self.api.current_target_data.get("hooks", None)
        if hooks_data == None:
            print("No hooks found for current target")
            return
        state_data = hooks_data.get(str(state), None)
        if state_data == None:
            print(str(state)+" state hook not found in PinFile")
            return
        print("current state data:: ", state_data)
        self.run_actions(state_data, target_data)
        for action in state_data:
            print(action)

    def run_actions(self, actions, target_data, is_global=False):
        """
        arguments
        actions: regardless of state the actions is list of actions performed .
        A sample action in yaml looks as follows :
        '''
        name: build_openshift_cluster
        type: ansible
        actions:
          - setup.yml
          - origin_from_source.yml
          - openshift_ansible_from_source.yml
          - deploy_aosi.yml
          - run_e2e_tests.yml
        '''
        target_data: data specific to target , which can be dict of topology , layout, outputs , inventory.
        is_global: scope of the hook.
        """
        if is_global:
            raise NotImplementedError("Run Hooks is not implemented \
                                       for global scoped hooks")
        else:
            for action in actions:
                action_type = action["type"]
                action_obj = ActionManager(action_type, action, target_data)
                action_obj.execute()

"""
p = ActionManager("imp1")
p.f("Hello world"); p.g(); p.h();
p = ActionManager("imp2")
p.f("Hello World2"); p.g(); p.h();
p = ActionManager("shell",{})
p.load("Hello");p.execute();
p = ActionManager("ansible", {})
p.load("Hello");p.execute();
p = ActionManager("imp3")
p.f(); p.g(); p.h();
"""

"""
Example of hook for a target
hooks:
  post-up:
    before_invgen:              # sub-state is specified
      - name: do_something      
        type: golang
        action_manager: golang_manager
        actions:
          - do_this.go
      - name: manipulate_inventory
        type: ansible
        path: my_ansible_stuff
        actions:
          - add_many_global_vars_so_i_dont_have_to_create_it_in_a_layout.yml
            vars_file: amgvsidhtciial.yml
      - name: check_ssh
      - name: build_openshift_cluster
        type: ansible
        actions:
          - setup.yml
          - origin_from_source.yml
          - openshift_ansible_from_source.yml
          - deploy_aosi.yml
          - run_e2e_tests.yml
  pre-down:
    - name: teardown_jenkins   # if no state it should take the default state into consideration
      type: python
      actions:
        - TOPO="{{ topology }}" /usr/bin/python2.7 paws group -n my_test.yml
"""

def run_actions(actions , target_data, is_global=False):
    """
    arguments
    actions: regardless of state the actions is list of actions performed .
    A sample action in yaml looks as follows :
    '''
      name: build_openshift_cluster
      type: ansible
      actions:
        - setup.yml
        - origin_from_source.yml
        - openshift_ansible_from_source.yml
        - deploy_aosi.yml
        - run_e2e_tests.yml
    '''
    target_data: data specific to target , which can be dict of topology , layout, outputs , inventory.
    is_global: scope of the hook.
    """
    if is_global:
        raise NotImplementedError("Run Hooks is not implemented \
                                   for global scoped hooks")
    else:
        for action in actions:
            action_type = action["type"]
            action_obj = ActionManager(action_type, action, target_data)
            action_obj.execute()

# testing runhooks
actions = [
        {"name": "somename", "type":"shell", "actions":['samvaran']},
        {"name": "somename", "type":"shell", "path": "/tmp/shellscripts", "actions":['thisisshell.sh']},
        {
             "name": "someothername",
             "type":"ansible",
             "path": "/tmp/",
             "actions":[
                 {
                     "playbook":'test.yml',
                     "vars":"test_vars.yaml",
                     "extra_vars": {
                         "testvar":"world"
                         }
                 }
             ],
        }
]
target_data = {
                 "topology":"/tmp/sometopology.yaml",
                 "layout":"/tmp/somelayout.yml",
                 "inventory":"/home/srallaba/workspace/venvs/pr189/linchtest/inventories/example_topo.inventory",
              }

#run_actions(actions, target_data)
