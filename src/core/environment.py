import json
import os
import zlib
from threading import Thread

from src.core.system import get_system_release, get_system_version, get_system_sha256
from src.utils.terminal import Terminal
from src.utils.dateutil import delay

class Environment:
    def __init__(self) -> None:
        self.terminal = Terminal()

        self.ENV_FILENAMES = os.path.join(os.getcwd(), "env.lnx")
        self.ENVIRONMENTS = {}
        
        self.isRunning = {}
        self.isRunning["read"] = True
        self.isRunning["write"] = True
        self.isRunning["threads"] = []

    def close(self):
        if self.isRunning["read"] is True:
            self.isRunning["read"] = False
        elif self.isRunning["read"] is False:
            self.terminal.console("thread can't stop", self.terminal.MESSAGE_WARNING, True, False)
        else: pass
        if self.isRunning["write"] is True:
            self.isRunning["write"] = False
        elif self.isRunning["write"] is False:
            self.terminal.console("thread can't stop", self.terminal.MESSAGE_WARNING, True, False)
        for thread in self.isRunning["threads"]:
            thread.join()

    def build_default_environment(self):
        if len(self.ENVIRONMENTS) != 1:
            self.ENVIRONMENTS["user"] = {}
            self.ENVIRONMENTS["root"] = {}
            self.ENVIRONMENTS["user"]["user"] = "demo"
            self.ENVIRONMENTS["user"]["pass"] = "1234"
            self.ENVIRONMENTS["root"]["version"] = get_system_version()
            self.ENVIRONMENTS["root"]["release"] = get_system_release()
            self.ENVIRONMENTS["root"]["system_sha256"] = get_system_sha256()

    def read(self):
        if os.path.isfile(self.ENV_FILENAMES):
            with open(self.ENV_FILENAMES, "rb") as File:
                content_byte = File.read()
                try:
                    zlib_decompiled = zlib.decompress(content_byte)
                    self.ENVIRONMENTS = json.loads(zlib_decompiled.decode())
                    File.close()
                except zlib.error:
                    self.build_default_environment()
                    return False
        else:
            self.build_default_environment()
            return False

    def readWithLooping(self, sec: int = 2):
        while self.isRunning["read"]:
            self.read()
            delay(sec)

    def readWithThread(self, sec: int = 2):
        th = Thread(target=self.readWithLooping, args=(sec, ))
        th.setDaemon(True)
        th.start()
        self.isRunning["threads"].append(th)

    def write(self):
        json_dumps = json.dumps(self.ENVIRONMENTS)
        zlib_compiled = zlib.compress(json_dumps.encode())
        File = open(self.ENV_FILENAMES, "wb")
        File.write(zlib_compiled)
        File.close()

    def writeWithLooping(self, sec: int = 2):
        while self.isRunning["write"]:
            self.write()
            delay(sec)
    
    def writeWithThread(self, sec: int = 2):
        th = Thread(target=self.writeWithLooping, args=(sec, ))
        th.setDaemon(True)
        th.start()
        self.isRunning["threads"].append(th)

    def update(self, key: str, value: str, isUser: bool = True):
        if isUser is True:
            self.ENVIRONMENTS["user"][key] = value

    def get(self, key: str):
        try:
            return self.ENVIRONMENTS["user"][key]
        except KeyError:
            return None

    def getRoot(self, key: str):
        try:
            return self.ENVIRONMENTS["root"][key]
        except KeyError:
            return None