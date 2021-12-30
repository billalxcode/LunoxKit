# Berfungsi untuk mendaftarkan semua module yang terpasang
# supaya bisa dijalakan

import os
import sys
import json
from glob import glob

try:
    from src.utils.terminal import print
    from src.utils.terminal import COLOR_GREEN, COLOR_WHITE, COLOR_RED, MESSAGE_WARNING
    from src.utils.utils import change_path_reg, check_path_syntax
except ImportError:
    from utils.terminal import print
    from utils.terminal import COLOR_GREEN, COLOR_WHITE, COLOR_RED, MESSAGE_WARNING
    from utils.utils import change_path_reg, check_path_syntax

UNKNOWN_ASCI_PATH = list("!@#$%^&*()+={}[]'?")

class RegisterModules:
    def __init__(self) -> None:
        self.PATHS = [
            "src/modules/*.json", "modules/*.json", "/usr/share/lunoxkit/modules/*.json"
        ]
        self.MODULES = None
        self.MODULE_INSTALLED = []

    @property
    def show_installed(self):
        return self.MODULE_INSTALLED

    @property
    def reg_list(self):
        lst = []
        for modules in self.MODULE_INSTALLED:
            lst.append(modules["reg"])
        return lst
        
    @property
    def is_null(self):
        length = len(self.MODULE_INSTALLED)
        if length == 0:
            return True
        else:
            return False

    def get_modules(self, paths: list = []):
        length = len(paths)
        if length == 0:
            return False
        
        for path in paths:
            with open(path, "r") as File:
                content = File.read()
                try:
                    self.MODULES = json.loads(content)
                    print(f"Getting all modules => {COLOR_GREEN}OK")
                    return True
                except (json.JSONDecodeError, json.decoder.JSONDecodeError):
                    self.MODULES = None
                    print(f"Getting all modules => {COLOR_RED}FAILED")
                    return False

    def find_filename(self):
        paths = []
        for path in self.PATHS:
            for glb in glob(path):
                paths.append(glb)
        self.get_modules(paths)

    def load_all(self):
        if self.MODULES is not None:
            try:
                for modules in self.MODULES["modules"]:
                    try:
                        MODNAME = modules["module"]
                        PACKAGE = modules["package"]
                        DEPS    = modules["deps"]
                        REG     = modules["reg"]
                        PACKAGE = change_path_reg(PACKAGE, MODNAME)
                        REG     = change_path_reg(REG, MODNAME)
                        regsts, regerr = check_path_syntax(REG, UNKNOWN_ASCI_PATH)
                        pathsts, patherr = check_path_syntax(PACKAGE, UNKNOWN_ASCI_PATH)
                        depserror = []
                        if len(DEPS) >= 1:
                            for deps in DEPS:
                                try:
                                    exec(f"import {deps}")
                                except:
                                    depserror.append(deps)
                        if len(depserror) >= 1:
                            depsrequire = ",".join(depserror)
                            print(f"Missing dependencies, require dependencies: {depsrequire}", MESSAGE_WARNING, False)
                            exit()
                        if regsts:
                            print(f"Module can't be load, unknown syntax reg '{regerr}'", MESSAGE_WARNING)
                            continue
                        if pathsts:
                            print(f"Module can't be load, unknown syntax package '{patherr}'", MESSAGE_WARNING)
                            continue
                        self.MODULE_INSTALLED.append({"modname": MODNAME, "package": PACKAGE, "reg": REG})
                        print(f"Load module '{REG}' => {COLOR_GREEN}OK")
                    except KeyError as key:
                        print(f"Module can't be load, {key} required key", MESSAGE_WARNING)
            except KeyError:
                print(f"Modules can't be load, syntax error!", MESSAGE_WARNING)
        else:
            print(f"Modules can't be load, check your installation modules!", MESSAGE_WARNING)