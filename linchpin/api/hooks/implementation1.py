import pdb

class Implementation1:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.args = args
    def f(self, test_var):
        print("Implementation1.f() "+test_var)
        print(self.kwargs)
    def g(self):
        print("Implementation1.g()")
    def h(self):
        print("Implementation1.h()")
