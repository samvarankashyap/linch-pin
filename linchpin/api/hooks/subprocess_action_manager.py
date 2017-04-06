import subprocess

class SubprocessActionManager:
    def __init__(self, name, action_data, target_data, *args, **kwargs):
        self.name = name
        self.action_data = action_data
        self.target_data = target_data
        self.args = args
        self.kwargs = kwargs

    def load(self):
        print("Load module of Subprocess Action Manager ")
        print("Action data "+str(self.action_data))
        print("Target data "+str(self.target_data))

    def add_params(self, action):
        command = action
        for key in self.target_data:
            command += " %s=%s " %(key, self.target_data[key])
        return command

    def execute(self):
        print("Execute module of SubprocessAction Manager")
        for action in self.action_data["actions"]:
            command = self.add_params(action)
            print command
            process = subprocess.call(command, shell=True)
            #process.wait()
            print process
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            proc.wait()
            for line in proc.stdout:
                print line
            #popen = subprocess.Popen([command], stdout=subprocess.PIPE,bufsize=1)
            #lines_iterator = iter(popen.stdout.readline, b"")
            #while popen.poll() is None:
            #    for line in lines_iterator:
            #        nline = line.rstrip()
            #        print(nline)
            #        sys.stdout.flush()
