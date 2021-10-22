from importlib import import_module
import json
import os
import sys
import time
import subprocess

class Build:
    def __init__(self) -> None:
        self.configFilename = os.path.join(os.getcwd() + "/setup.json")
        self.timeDelay = 0.1

    #=== Load Configuration File ===#
    def loadConfig(self):
        if os.path.isfile(self.configFilename) is True:
            print (f"INFO: Config path '{self.configFilename}'")
            with open(self.configFilename) as F:
                content = F.read()
                try:
                    contentJson = json.loads(content)
                    self.config = contentJson
                    try:
                        self.timeDelay = self.config["timeDelay"]
                    except KeyError:
                        self.timeDelay = 0.1
                except json.JSONDecodeError:
                    print ("ERROR: Cannot load config")
                    sys.exit()
        else:
            print ("ERROR: No config file")
            sys.exit()

    def installModule(self, name: str = ""):
        print (f"Installing module {name}...")
        commands = [self.config['cmd']['pip'], "install", name]
        subprocess.call(commands, stdout=subprocess.PIPE)

    def loadModules(self):
        requirements = self.config["requirements"]
        for requirement in requirements:
            print (f"Looking requirement '{requirement}'")
            if requirement == "pyinstaller":
                requirement = "PyInstaller"
            try:
                import_module(name=requirement)
            except ModuleNotFoundError:
                self.installModule(requirement)

    def delay(self):
        time.sleep(self.timeDelay)

    def showinfo(self):
        requirements = ", ".join(self.config["requirements"])
        cmds = ", ".join(self.config["cmd"])
        print (f"Tools name: {self.config['name']}")
        self.delay()
        print (f"Version code: {self.config['version']}")
        self.delay()
        print (f"Requirements: {requirements}")
        self.delay()
        print (f"Command Require: {cmds}")
        self.delay()
        print (f"Platform: {sys.platform}")
        self.delay()

    def start(self):
        self.loadConfig()
        self.showinfo()
        self.loadModules()

if __name__ == "__main__":
    script = Build()
    script.start()