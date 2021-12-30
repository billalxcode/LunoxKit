import json
import os

from src.utils.terminal import Terminal

class Config:
    def __init__(self) -> None:
        self.CONFIG_FILENAME = os.path.join(os.getcwd(), "config.json")
        self.config_data = {}

        self.terminal = Terminal()
        self.STDINFO = self.terminal.info
        self.STDERR = self.terminal.error

    def read(self):
        if os.path.isfile(self.CONFIG_FILENAME):
            with open(self.CONFIG_FILENAME, "r") as File:
                content = File.read()
                try:
                    self.config_data = json.loads(content)
                except (json.JSONDecodeError):
                    self.terminal.console("Json error, can't load json.", self.STDERR, True, True)
        else:
            filename = os.path.basename(self.CONFIG_FILENAME)
            self.terminal.console(f"'{filename}' No such file or directory", self.STDERR, True, True)

