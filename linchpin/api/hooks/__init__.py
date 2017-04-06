#proxy pattern implementation

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
            action_obj.load()
            action_obj.execute()

# testing runhooks
actions = [
        {"name": "somename", "type":"shell", "path": "/tmp/", "actions":['samvaran']},
        {"name": "someothername", "type":"ansible", "path": "/tmp/", "actions":['test.yml']}
        ]
target_data = {"topology":"/tmp/sometopology.yaml", "layout":"/tmp/somelayout.yml"}

run_actions(actions, target_data)
