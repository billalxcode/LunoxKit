import os
import re
import readline
from threading import Thread

from src.core.environment import Environment
from src.modules.registerModules import RegisterModules
from src.utils.terminal import Terminal
from src.utils.terminal import MESSAGE_ERROR, MESSAGE_INFO, MESSAGE_NORMAL, MESSAGE_WARNING
from src.utils.terminal import COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_WHITE, COLOR_CYAN, COLOR_RESET, COLOR_YELLOW
from src.utils.utils import change_prompt_syntax
from src.utils.dateutil import delay
from src.core.handler import CommandHandler
from src.core.completer import Completer

class Shell:
    def __init__(self) -> None:
        self.DEFAULT_PROMPT = f"{COLOR_GREEN}Lunoxkit{COLOR_WHITE}:{COLOR_CYAN}[module]{COLOR_RESET}$ "
        self.PROMPT         = self.DEFAULT_PROMPT
        self.MODULE         = ""

        self.regmod         = RegisterModules()
        self.environment    = Environment()
        self.terminal       = Terminal(environment=self.environment)
        self.handler        = CommandHandler(self.terminal, self.regmod, self)
        self.completer_     = Completer()

        self.threadRunning  = True
        self.threads = {
            "completer": None,
        }
        self.current_directory = []

    def destroy(self):
        self.threadRunning = False
        for thread in self.threads:
            self.threads[thread].join()
        self.environment.close()
        self.terminal.quit()

    def initialize(self):
        self.regmod.find_filename()
        self.regmod.load_all()
        self.terminal.console("All in done.", MESSAGE_INFO)
        self.environment.readWithThread()
        self.environment.writeWithThread()
        self.handler.initialize()

        prompt_string = self.environment.get("prompt")
        if prompt_string is not None:
            self.PROMPT = prompt_string
        else: pass

    def completer(self, text, state):
        directory = self.handler.action.build_completer()

        modules = [f"use module {item['reg']}" for item in self.regmod.MODULE_INSTALLED]
        commands = self.handler.commands
        commands.extend(modules)
        commands.extend(self.handler.command_with_params)
        commands.extend(directory)
        options = [i for i in commands if i.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

    def setup_autocomplete(self, sec: int = 1):
        while self.threadRunning:
            commands = self.handler.commands
            commands.extend(self.handler.command_with_params)
            # print (self.completer_.COMMANDS)
            readline.set_completer_delims('')
            readline.parse_and_bind("tab:complete")
            readline.set_completer(self.completer)
            delay(sec)

    def user_input(self, prompt):
        try:
            result = input(prompt)
        except KeyboardInterrupt:
            self.threadRunning = False
            self.threads["completer"].join()
            print()
            self.terminal.quit()
        return result

    def run(self):
        th = Thread(target=self.setup_autocomplete, args=(1, ))
        th.start()
        self.threads["completer"] = th

        while True:
            module = self.handler.get_module
            used_module = ("~" if module == "system" else f"{module}/")
            prompt_syntax = change_prompt_syntax(self.PROMPT, used_module)
            result_input = self.user_input(prompt_syntax)
            command, arguments = self.handler.parse_input(result_input)
            self.handler.handle_command(command, arguments)