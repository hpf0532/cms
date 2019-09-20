from django.test import TestCase

# Create your tests here.

APP_TEST = "dslagjd"

class Test(object):
    def __init__(self, name=None):
        self.name = name


a = Test(name=APP_TEST)
print(type(a.name))