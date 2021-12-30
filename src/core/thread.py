import threading
from typing import Callable

class Thread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        self.name = ""
        self.thid = 0
        self.target = None
        self.group = None
        self.args = ()

    @property
    def getid(self):
        return self.thid

    @property
    def getname(self):
        return self.name

    def set_target(self, func):
        self.target = func

    def set_args(self, args):
        self.args = args

    def set_group(self, group):
        self.group = group
