from __init__ import LinchpinAPI as lapi
context = {
        "workspace": "/tmp/"
        }

class Context:
    def __init__(self):
        self.workspace = "/tmp/"

context = Context()

test = lapi(context)
test.lp_rise("test.yaml", [])
