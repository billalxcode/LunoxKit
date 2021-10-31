import os
import sys
moduleDir = os.path.join(os.getcwd(), "src")
sys.path.insert(0, moduleDir)
from .terminal import Terminal
from .handler import Handler

class Apps:
    def __init__(self) -> None:
        self.terminal = Terminal()
        self.handler  = Handler()

    def run(self):
        while True:
            try:
                self.terminal.clear()
                self.terminal.showLogo()
                self.terminal.showMenu()
                i = self.terminal.question("Select > ")
                if i == "0" or i == "00":
                    self.terminal.quit(newLine=False)
                elif i == "1" or i == "01":
                    try:
                        #from .plugin import bruteSubdo
                        from .plugin import bruteSubdo
                        bruteSubdo.run()
                    except ImportError as e:
                        if e.name is None:
                            self.handler.moduleError(e.msg, unknownParrent=True)
                        else:
                            self.handler.moduleError(e.name, importError=True)
                    except ModuleNotFoundError as e:
                        self.handler.moduleError(e.msg, moduleNotFound=True)
                    except SyntaxError as e:
                        self.handler.moduleError(e.msg, syntaxError=True)
                elif i == "2" or i == "02":
                    try:
                        from .wordlist import Wordlist
                        self.terminal.clear()
                        self.terminal.showLogo()
                        wordlist = Wordlist()
                        wordlist.selectManifest()
                    except ImportError as e:
                        if e.name is None:
                            self.handler.moduleError(e.msg, unknownParrent=True)
                        else:
                            self.handler.moduleError(e.name, importError=True)
                    except ModuleNotFoundError as e:
                        self.handler.moduleError(e.msg, moduleNotFound=True)
                    except SyntaxError as e:
                        self.handler.moduleError(e.msg, syntaxError=True)
                elif i == "3" or i == "03":
                    try:
                        from .plugin import adminFinder
                        adminFinder.run()
                    except ImportError as e:
                        if e.name is None:
                            self.handler.moduleError(e.msg, unknownParrent=True)
                        else:
                            self.handler.moduleError(e.name, importError=True)
                    except ModuleNotFoundError as e:
                        self.handler.moduleError(e.msg, moduleNotFound=True)
                    except SyntaxError as e:
                        self.handler.moduleError(e.msg, syntaxError=True)
                elif i == "4" or i == "04":
                    try:
                        from modules import exploitModules
                        exploitModules.run()
                    except ImportError as e:
                        if e.name is None:
                            self.handler.moduleError(e.msg, unknownParrent=True)
                        else:
                            self.handler.moduleError(e.name, importError=True)
                    except ModuleNotFoundError as e:
                        self.handler.moduleError(e.msg, moduleNotFound=True)
                    except SyntaxError as e:
                        self.handler.moduleError(e.msg, syntaxError=True)
            except KeyboardInterrupt:
                self.terminal.quit(newLine=True)
