class Shortcut:
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

    """
    Given a dictionary of key shortcuts to replacements, replaces the operators.
    e.g.: {("rcmd", "lctrl", "ralt"): ("fn", "lctrl")}
    """
    def replace_operators(self, opmap):
        for k, v in opmap.items():
            if all([i in self.operators for i in k]):
                for i in k:
                    self.operators.remove(i)
                for i in v:
                    self.operators.append(i)

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

    def parse(self, opmap=None):
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
                if opmap:
                    sh.replace_operators(opmap)

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
    import argparse
    import os
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Parse skhdrc keyboard shortcuts and commands")
    parser.add_argument('--file', '-f', default=os.path.join(Path.home(), ".skhdrc"), help='skhdrc file')
    parser.add_argument('--output', '-o', default=None, help='output format')
    args = parser.parse_args()

    import pprint

    # rcmd + lctrl + ralt as specified in skhd config is mapped to fn + lctrl
    opmap = {("rcmd", "lctrl", "ralt"): ("fn", "lctrl")}

    p = Parser(args.file)
    parse = p.parse(opmap=opmap)

    if args.output == 'json':
        jsondata = {
            "comments": {str(k): v for k, v in parse[0].items()},
            "commands": {str(k): v for k, v in parse[1].items()}
        }
        print(json.dumps(jsondata, indent=2))