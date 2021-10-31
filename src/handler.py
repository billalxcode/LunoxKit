from .terminal import Terminal

class Handler:
    def __init__(self) -> None:
        self.terminal = Terminal()

    def moduleError(self, message: str = "", 
                    moduleNotFound: bool = False, 
                    syntaxError: bool = False, 
                    importError: bool = False,
                    unknownParrent: bool = False
        ):
        if moduleNotFound:
            self.terminal.console(f"Module '{message}' not found, please install 'pip3 install {message}'", "error")
            self.terminal.quit(isUser=False)
        elif syntaxError:
            self.terminal.console(f"syntax '{message}' error", "error")
            self.terminal.quit(isUser=False)
        elif importError:
            self.terminal.console(f"Failed import module '{message}'", "error")
            self.terminal.quit(isUser=False)
        elif unknownParrent:
            self.terminal.console(f"{message.capitalize()}", "error")
            self.terminal.quit(isUser=False)

    def connectionError(self, host: str = "", port: int = 80, timeout: int = 30, isQuit: bool = False):
        self.terminal.console(f"Failed to connect '{host}' at port '{port}", "error")
        if isQuit:
            self.terminal.quit(isUser=False)
        