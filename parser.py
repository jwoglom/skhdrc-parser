class Shortcut:
    BASE = ["cmd", "ctrl", "alt"]

    def __init__(self, text):
        self.mode = None
        self.text = text
        self.operators = []
        self.added_operators = []
        self.key = None
        self.parse()

    def parse(self):
        parts = [i.strip() for i in self.text.split("-")]
        if len(parts) == 2:
            operators, key = parts
        else:
            operators = parts[0]
            key = ''

        if "<" in operators:
            mode, operators = operators.split("<", 1)
            self.mode = mode.strip()

        if operators.startswith("::"):
            mode = operators.split("::", 1)[1]
            self.mode = mode.strip()
            operators = ""

        self.operators = [i.strip() for i in operators.split("+")]
        self.key = key

        if not self.key and len(self.operators) == 1:
            self.key = self.operators[0]
            self.operators = []

        ops = [i for i in self.operators]
        if all([b in ops for b in self.BASE]):
            for b in self.BASE:
                ops.remove(b)
        self.added_operators = ops

    def __str__(self):
        s = ""
        if self.mode:
            s += "[%s] " % self.mode if self.mode else ""
        if self.operators:
            s += "+".join(self.operators)
        if self.key:
            if self.operators:
                s += " - "
            s += self.key
        return s.strip()

    def __repr__(self):
        return "Shortcut(%s)" % self.__str__()

    def __eq__(self, other):
        return self.operators == other.operators and self.key == other.key

    def __hash__(self):
        return hash(tuple([tuple(self.operators), tuple(self.key)]))

class Parser:
    def __init__(self, file):
        self.file = file

    def readlines(self):
        lines = open(self.file, "r").read().splitlines()
        return [l.strip() for l in lines]

    def parse(self):
        comments = {}
        commands = {}
        curComment = []
        continueSh = None
        for line in self.readlines():
            line = line.strip()
            if line.startswith("#"):
                curComment.append(line.split("#", 1)[1].strip())
                continue
            if line == "":
                curComment = []
                continue
            if continueSh:
                commands[continueSh] += "\n" + line
                if not line.endswith("\\"):
                    continueSh = None
            if " : " in line:
                keys, cmd = line.split(" : ", 1)
                sh = Shortcut(keys)
                if cmd.endswith("\\"):
                    continueSh = sh
                commands[sh] = cmd
                comments[sh] = ("\n".join(curComment)).strip()
                curComment = []
            elif " ; " in line:
                # Hack into the command output, for now
                keys, modeSwitch = line.split(" ; ", 1)
                sh = Shortcut(keys)
                commands[sh] = "modeswitch %s" % modeSwitch
                comments[sh] = ("\n".join(curComment)).strip()
                curComment = []

        return comments, commands


if __name__ == '__main__':
    import os
    from pathlib import Path
    import pprint

    skhdrc = os.path.join(Path.home(), ".skhdrc")
    p = Parser(skhdrc)
    print(pprint.pprint(p.parse()))