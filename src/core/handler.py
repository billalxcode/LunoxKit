import os
import pathlib
from typing import Callable
from glob import glob
from colorama import Fore

from src.utils.terminal import Terminal
from src.utils.terminal import MESSAGE_NORMAL, MESSAGE_ERROR, MESSAGE_WARNING, MESSAGE_INFO
from src.utils.terminal import COLOR_BLUE, COLOR_RESET
from src.core.system import get_system_sha256, get_system_version, get_system_release
from src.core.completer import Completer
from src.modules.registerModules import RegisterModules
from src.modules.handleModule import Handler
from src.utils.utils import (
    getcwd, isfile, path_join, basename, isdir, mkdir, 
    rmdir
)

class RegisterCommand:
    def __init__(self, terminal: Terminal) -> None:
        self.terminal  = terminal
        # self.commands  = []
        self.commands = {
        }
        self.arguments = []

    def find_command(self, key: str, command: str):
        data = []
        if key in self.commands:
            for keys in self.commands[key]:
                print (keys)
        else:
            return False
            
    def register(self, key: str):
        if key in self.commands:
            self.terminal.console(f"Key '{key}' already exists", MESSAGE_ERROR, False, afterQuit=True)
        else:
            self.commands[key] = []

    @property
    def command_with_params(self):
        result = []
        for keys in self.commands:
            for item in self.commands[keys]:
                if item["params"] is None: continue
                else:
                    for param in list(item['params']):
                        output = f"{item['command']} {param}"
                        result.append(output)
        return result
        
    @property
    def cmdlist(self):
        result = []
        for keys in self.commands:
            for value in self.commands[keys]:
                result.append(value["command"])
        return result

    @property
    def arglist(self):
        return self.arguments

    # def removeArgument(self, command: str = None, arg: str = ""):
    #     if command is None and arg != "":
    #         if arg in self.arguments:
    #             self.arguments.remove(arg)
    #             return True
    #         else: return False
    #     elif command is not None and arg != "":
    #         join_string = f"{command} {arg}"
    #         if join_string in self.arguments:
    #             self.arguments.remove(join_string)
    #         else: return False

    def exists(self, cmd: str, module: str):
        for command in self.commands[module]:
            if cmd == command["command"]:
                return True
        for command in self.commands["system"]:
            if cmd == command["command"]:
                return True

    def register_argument(self, command: str = None, argument: str = ""):
        if command is None and argument != "":
            self.arguments.append(argument)
            return True
        elif command is not None and argument != "":
            self.arguments.append(f"{command} {argument}")
            return True

    def handle(self, key: str, command: str, callback: Callable, params: tuple = None):
        if key in self.commands:
            new_command = {"command": command, "callback": callback, "params": params}
            self.commands[key].append(new_command)
        else:
            self.terminal.console(f"Key '{key}' not found", MESSAGE_ERROR, False, afterQuit=True)
            return False

    def execute(self, command: str, argument: tuple = (), module: str = ""):
        for cmds in self.commands[module]:
            try:
                if command == cmds["command"]:
                    arg = {"user": argument, "root": cmds["params"], "command": command}
                    callback = cmds["callback"]
                    callback(arg)
                    return True
            except TypeError as err:
                self.terminal.console(f"{err}", MESSAGE_ERROR, False)
                return False
            except RecursionError:
                self.terminal.console(f"Unable to call function.", MESSAGE_ERROR, False)
                return False
        return self.execute(command, argument, "system")

class Action:
    def __init__(self, terminal: Terminal, modhandler: Handler, regcmd: RegisterCommand, shell) -> None:
        self.terminal    = terminal
        self.modhandler  = modhandler
        self.regcmd      = regcmd
        self.shell       = shell

        self.USED_MODULE = "system"
        self.DIR         = pathlib.Path(path_join(getcwd(), "data"))
        self.DIR_ROOT    = self.DIR

    @property
    def get_module(self):
        return self.USED_MODULE

    def build_completer(self):
        completer = []
        for glb in self.DIR.glob("*"):
            completer.append(f"cd {basename(glb)}")
        completer.append(f"cd ..")
        return completer

    def quit(self, argument: dict = {}):
        self.shell.destroy()
        self.terminal.quit()

    def clear(self, argument: dict = {}):
        self.terminal.clear()

    def get_sha256(self, argument: dict = {}):
        sha256 = get_system_sha256()
        self.terminal.console(sha256, MESSAGE_NORMAL, False)
        return sha256

    def system_release(self, argument: dict = {}):
        release = get_system_release()
        self.terminal.console(release, MESSAGE_NORMAL, False)
        return release

    def system_version(self, argument: dict = {}):
        version = get_system_version()
        self.terminal.console(version, MESSAGE_NORMAL, False)
        return version

    def onUse(self, argument: dict = {}):
        user_argument = argument["user"]
        if user_argument is None: return False
        
        argument_length = len(user_argument)
        if argument_length == 0:
            self.terminal.console(f"use <type> <value>", MESSAGE_NORMAL, False)
            return False
        else:
            if user_argument[0] == "module":
                if argument_length == 2:
                    module_name = user_argument[1]
                    module_available = self.modhandler.find_module(module_name)
                    if module_available is True:
                        self.modhandler.set_current(module_name)
                        isRunning = self.modhandler.run(self.regcmd)
                        if isRunning is False:
                            self.onRemove()
                            return False
                        else:
                            self.USED_MODULE = module_name
                            return True
                    else:
                        self.terminal.console(f"No '{module_name}' modules are available", MESSAGE_NORMAL, False)
                        return False
                else:
                    self.terminal.console(f"Module name required", MESSAGE_NORMAL, False)
                    return False
            else:
                self.terminal.console(f"Unknown argument '{user_argument[0]}'", MESSAGE_NORMAL, False)
                return False

    def onRemove(self, argument: dict = {}):
        if self.USED_MODULE == "system": return False
        else:
            del self.regcmd.commands[self.USED_MODULE]
        self.USED_MODULE = "system"
        
    def onChangeDirectory(self, argument: dict = {}):
        user_argument = argument["user"]
        if user_argument is None:
            root = self.DIR_ROOT
            self.DIR = pathlib.Path(root)
            return False
        argument_length = len(user_argument)
        if argument_length == 0:
            root = self.DIR_ROOT
            self.DIR = pathlib.Path(root)
            return False
        elif argument_length == 1:
            if user_argument[0].strip() == "":
                root = self.DIR_ROOT
                self.DIR = pathlib.Path(root)
                return False
            elif user_argument[0] == "..":
                parent = self.DIR.parent
                self.DIR = pathlib.Path(parent)
                return True
            else:
                new_path = path_join(self.DIR, user_argument[0])
                if isdir(new_path):
                    self.DIR = pathlib.Path(new_path)
                    return True
                else:
                    self.terminal.console(f"{user_argument[0]}: No such file or directory", MESSAGE_NORMAL, False)
                    return False

    def onMakeDir(self, argument: dict = {}):
        user_argument = argument["user"]
        if user_argument is None:
            self.terminal.console(f"mkdir: missing operand", MESSAGE_NORMAL, False)
            return False
        else:
            for destination_dir in user_argument:
                if destination_dir == "": 
                    self.terminal.console(f"mkdir: missing operand", MESSAGE_NORMAL, False)
                    break
                
                dest = path_join(self.DIR, destination_dir)
                if isdir(dest):
                    self.terminal.console(f"mkdir: cannot create directory '{destination_dir}': File exists")
                else:
                    mkdir(dest)

    def onListFile(self, argument: dict = {}):
        if isdir(self.DIR):
            direction = path_join(self.DIR, "*")
            listfiles = glob(direction)
            output = []
            for files in listfiles:
                if isdir(files):
                    output.append(f"{COLOR_BLUE}{basename(files)}")
                elif isfile(files):
                    output.append(f"{COLOR_RESET}{basename(files)}")
            output = "  ".join(output)
            self.terminal.console(output, MESSAGE_NORMAL, False)
            return True
        else:
            self.terminal.console(f"{basename(self.DIR)}: No such directory", MESSAGE_NORMAL, False)
            return False
            
    def onCat(self, argument: dict = {}):
        user_argument = argument['user']
        if user_argument is None:
            self.terminal.console(f"cat <filename>", MESSAGE_NORMAL, False)
            return False
        else:
            argument_length = len(user_argument)
            if argument_length == 0 or argument_length > 3:
                self.terminal.console(f"cat <filename>", MESSAGE_NORMAL, False)
                return False
            else:
                filename = path_join(self.DIR, user_argument[0])
                if isfile(filename):
                    with open(filename, "r") as File:
                        while True:
                            data = File.read(1024)
                            if not data: break
                            else:
                                print(data)
                elif isdir(filename):
                    self.terminal.console(f"{basename(filename)}: Is a directory", MESSAGE_NORMAL, False)
                    return False
                else:
                    self.terminal.console(f"{basename(filename)}: No such file or directory", MESSAGE_NORMAL, False)
                    return False

    def onRemovedirs(self, argument: dict = {}):
        user_argument = argument["user"]
        command = argument["command"]
        if user_argument is None:
            self.terminal.console(f"{command}: missing operand", MESSAGE_NORMAL, False)
            return False
        else:
            for destination_source in user_argument:
                if destination_source == "":
                    self.terminal.console(f"{command}: missing operand", MESSAGE_NORMAL, False)
                    break
                else:
                    dest = path_join(self.DIR, destination_source)
                    if isdir(dest):
                        rmdir(dest)
                    elif isfile(dest):
                        self.terminal.console(f"{command}: cannot remove '{dest}': Is a file", MESSAGE_NORMAL, False)
                    else:
                        self.terminal.console(f"{command}: cannot remove '{dest}': No such file or directory", MESSAGE_NORMAL, False)
                        
class CommandHandler:
    def __init__(self, terminal: Terminal, regmod: RegisterModules, shell) -> None:
        self.terminal = terminal
        self.regmod = regmod
        self.shell = shell
        self.regcmd = RegisterCommand(self.terminal)
        self.modhandler = Handler()
        self.action = Action(self.terminal, self.modhandler, self.regcmd, self.shell)
        self.completer = Completer()
        
    @property
    def commands(self):
        return self.regcmd.cmdlist

    @property
    def command_with_params(self):
        return self.regcmd.command_with_params
        
    @property
    def get_module(self):
        return self.action.get_module

    def initialize(self):
        self.modhandler.MODULE_INSTALLED = self.regmod.MODULE_INSTALLED
        self.regcmd.register("system")
        self.regcmd.handle("system", "clear", self.action.clear)
        self.regcmd.handle("system", "quit", self.action.quit)
        self.regcmd.handle("system", "exit", self.action.quit)
        self.regcmd.handle("system", "lsb_sha256", self.action.get_sha256)
        self.regcmd.handle("system", "lsb_version", self.action.system_version)
        self.regcmd.handle("system", "lsb_release", self.action.system_release)
        self.regcmd.handle("system", "use", self.action.onUse, ("module"))
        self.regcmd.handle("system", "back", self.action.onRemove)
        self.regcmd.handle("system", "ls", self.action.onListFile)
        self.regcmd.handle("system", "cd", self.action.onChangeDirectory, tuple(self.completer.complete_path(self.action.DIR)))
        self.regcmd.handle("system", "cat", self.action.onCat, tuple(self.completer.complete_path(self.action.DIR)))
        self.regcmd.handle("system", "mkdir", self.action.onMakeDir)
        self.regcmd.handle("system", "rmdir", self.action.onRemovedirs, tuple(self.completer.complete_path(self.action.DIR)))

    def set_module(self, new_module: str):
        self.USED_MODULE = new_module

    def parse_input(self, user_input: str):
        string_split = user_input.split(" ")
        string_length = len(string_split)
        if string_length == 0:
            return None, None
        elif string_length == 1:
            return string_split[0], None
        elif string_length >= 2:
            return string_split[0], string_split[1:]

    def handle_command(self, command: str, arguments: tuple):
        cmd = command.strip() # Delete whitespace
        if cmd == "": return False
        cmd_exists = self.regcmd.exists(cmd, self.action.get_module)
        if cmd_exists:
            self.regcmd.execute(cmd, arguments, self.action.get_module)
            return True
        else:
            self.terminal.console(f"{cmd}: command not found", self.terminal.normal, False)
            return False