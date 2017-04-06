class Implementation2:
    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs
    def f(self, test_var):
        print("Implementation2.f() "+test_var)
    def g(self):
        print("Implementation2.g()")
    def h(self):
        print("Implementation2.h()")
