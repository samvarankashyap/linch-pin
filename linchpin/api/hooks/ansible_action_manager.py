class AnsibleActionManager:
    def __init__(self, name, action_data, target_data, *args, **kwargs):
        self.name = name
        self.action_data = action_data
        self.target_data = target_data
        self.args = args
        self.kwargs = kwargs

    def load(self):
        print("Load module of Ansible Action Manager ")
        print("Action data "+str(self.action_data))
        print("Target data "+str(self.target_data))

    def execute(self):
        print("Execute module of Ansible Action Manager")
