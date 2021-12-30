# Handle exceptions
class LunoxException(Exception):
    def __init__(self, message):
        self.message = message
    
    @property
    def getError(self):
        return "LunoxException"
        
    def __str__(self) -> str:
        return f"{self.message}"

class TerminalConsoleException(Exception):
    def __init__(self, message):
        self.message = message

    @property
    def getError(self):
        return "TerminalConsoleException"

    def __str__(self) -> str:
        return f"{self.message}"
