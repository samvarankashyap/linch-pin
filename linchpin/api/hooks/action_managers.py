from implementation1 import Implementation1
from implementation2 import Implementation2
from subprocess_action_manager import SubprocessActionManager
from ansible_action_manager import AnsibleActionManager
ACTION_MANAGERS = {
    "imp1" : Implementation1,
    "imp2" : Implementation2,
    "shell" : SubprocessActionManager,
    "ansible" : AnsibleActionManager
}
