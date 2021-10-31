import os
import sys

moduleDir = os.path.join(os.getcwd())
sys.path.insert(0, moduleDir)

class Backdoors:
    def __init__(self) -> None:
        from src.terminal import Terminal

        self.terminal = Terminal()

    def start(self):
        while True:
            self.terminal.clear()
            self.terminal.showLogo()
            if self.terminal.showNoImplement():
                break
    
def run():
    apps = Backdoors()
    apps.start()