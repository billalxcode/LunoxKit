import glob
import json
from src.utils.terminal import print
from src.utils.terminal import MESSAGE_WARNING

class PluginManager:
    def __init__(self):
        self.PATHS = [
            "src/modules/*.json", "modules/*.json", "/usr/share/lunoxkit/modules/*.json"
        ]
        self.REAL_PATH = self.find_filename()
        self.DATA = []

    def find_filename(self):
        # Build and find modules tree
        paths = []
        for path in self.PATHS:
            for files in glob.glob(path):
                paths.append(files)
        return paths

    def read_config(self):
        length = len(self.REAL_PATH)
        if length == 0:
            return False
        for files in self.REAL_PATH:
            with open(files, "r") as File:
                content = File.read()
                try:
                    modules = json.loads(content)
                    for module in modules:
                        try:
                            MODNAME = module["module"]
                            PACKAGE = module["package"]
                            DEPENDENCES = module["deps"]
                            REGMOD = module["reg"]
                        except KeyError as key:
                            print(f"Module can't be load, {key} required key", MESSAGE_WARNING)
                except (json.JSONDecodeError, json.decoder.JSONDecodeError):
                    self.DATA = None