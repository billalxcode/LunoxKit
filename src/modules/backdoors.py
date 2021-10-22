import os
import sys

moduleDir = os.path.join(os.getcwd(), "/src")
sys.path.insert(0, moduleDir)

class Backdoors:
    def __init__(self) -> None:
        pass

    def start(self):
        pass
    
def run():
    apps = Backdoors()
    apps.start()