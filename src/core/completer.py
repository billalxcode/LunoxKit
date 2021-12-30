import os
import re
import readline

class Completer(object):
    def __init__(self) -> None:
        super().__init__()

        self.COMMANDS = []
        self.SPACE_PATTERN = re.compile(".*\s+$", re.M)

    def set_commands(self, text: str):
        self.COMMANDS.append(text)
        return True

    def _listdir(self, root):
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def complete_path(self, path=None):
        if not path:
            return self._listdir(".")
        dirname, rest = os.path.split(path)
        temp = dirname if dirname else "."
        res = [
            os.path.join(dirname, p)
            for p in self._listdir(temp)
        ]
        if len(res) > 1 or not os.path.exists(path): return res
        if os.path.isdir(path):
            return [
                os.path.join(path, p)
                for p in self._listdir(path)
            ]
        return [path + " "]

    def complete_extra(self, args=None):
        if not args:
            return self.complete_path(".")
        return self.complete_path(args[-1])
    
    def complete(self, text, state):
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        if not line:
            return [c + " " for c in self.COMMANDS]
        if self.SPACE_PATTERN.match(buffer):
            line.append("")
        cmd = line[0].strip()
        if cmd in self.COMMANDS:
            impl = getattr(self, f"complete_{cmd}")
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + " "][state]
        results = [
            c + " "
            for c in self.COMMANDS
        ]
        return results[state]
