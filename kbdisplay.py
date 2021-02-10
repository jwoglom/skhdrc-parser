class Key:
    def __init__(self, disp, code=None, width=1, modifier=False):
        self.disp = disp
        self.code = code or disp
        self.width = width
        self.modifier = modifier

    def __str__(self):
        if self.code != self.disp:
            return "%s (%s)" % (self.disp, self.code)
        return self.disp
    
    def __repr__(self):
        return "Key(%s)" % self.__str__()

    def __eq__(self, o):
        return o.code.lower() == self.code.lower() and o.modifier == self.modifier
    
    @staticmethod
    def shortcut_list(sh):
        keys = []
        for s in sh.operators:
            keys.append(Key(s, modifier=True))

        if sh.key:
            keys.append(Key(sh.key))
        
        return keys
        

class KeyboardRow:
    ROW_WIDTH = 14.5

    TEXT_INVERT = '\033[0;30m\033[47m'
    TEXT_NORMAL = '\033[0m'

    def __init__(self, *keys, highlight=None):
        self.keys = keys
        self.highlight = highlight or []

        w = sum([k.width for k in keys])
        if w != self.ROW_WIDTH:
            raise Exception('KeyboardRow has incorrect width (%d)' % w)

    def __str__(self):
        return self.render_1x()

    def with_highlight(self, st, txt, end, apply=True):
        s = ""
        s += st
        s += self.TEXT_INVERT if apply else ""
        s += txt
        s += self.TEXT_NORMAL if apply else ""
        s += end

        return s

    """single-line representation of the row"""
    def render_1x(self, highlight=None):
        WIDTH_PER_PIXEL = 0.25
        highlight = highlight or self.highlight

        s = ""
        for k in self.keys:
            w = int(k.width / WIDTH_PER_PIXEL)
            s += self.with_highlight("[", k.disp[:(w-2)].center(w-2), "]", apply=k in highlight)

        return s

    """multi-line representation of the row. each row is 3 lines, width is shrunk by 1/size"""
    def render(self, size=8, highlight=None):
        if size == 4:
            return self.render_1x(highlight=highlight)

        if size % 4 != 0:
            raise Exception('Size must be a multiple of 4')

        highlight = highlight or self.highlight

        # For full 1:1 translation, use 1/12
        WIDTH_PER_PIXEL = (1 / size)
        BOX = [['┌', '─', '┐'],
               ['│', ' ', '│'],
               ['└', '─', '┘'],
               ['├', '─', '┤']]

        def process_highlight(k, st, txt, end):
            return self.with_highlight(st, txt, end, apply=k in highlight)

        s = ""
        for k in self.keys:
            w = int(k.width / WIDTH_PER_PIXEL)
            s += process_highlight(k, BOX[0][0], BOX[0][1] * (w-2), BOX[0][2])

        s += "\n"
        for k in self.keys:
            w = int(k.width / WIDTH_PER_PIXEL)
            s += process_highlight(k, BOX[1][0], k.disp[:(w-2)].center(w-2), BOX[1][2])

        s += "\n"
        for k in self.keys:
            w = int(k.width / WIDTH_PER_PIXEL)
            s += process_highlight(k, BOX[2][0], BOX[2][1] * (w-2), BOX[2][2])

        return s

class Keyboard:
    def __init__(self, *rows, scale=4):
        self.rows = rows
        if scale not in (4, 8, 12):
            raise Exception('Unsupported scale')
        self.scale = scale

    def __str__(self):
        return self.render(self.scale)

    def render(self, scale, highlight=None):
        s = ""
        for r in self.rows:
            s += "%s\n" % r.render(size=scale, highlight=highlight)
        return s

MAC_KB = Keyboard(
    KeyboardRow(
        Key("~"),
        Key("1"),
        Key("2"),
        Key("3"),
        Key("4"),
        Key("5"),
        Key("6"),
        Key("7"),
        Key("8"),
        Key("9"),
        Key("0"),
        Key("-"),
        Key("+"),
        Key("delete", width=1.5),
    ), KeyboardRow(
        Key("tab", width=1.5),
        Key("q"),
        Key("w"),
        Key("e"),
        Key("r"),
        Key("t"),
        Key("y"),
        Key("u"),
        Key("i"),
        Key("o"),
        Key("p"),
        Key("[", code="0x21"),
        Key("]", code="0x1E"),
        Key("\\")
    ), KeyboardRow(
        Key("capslock", width=1.75),
        Key("a"),
        Key("s"),
        Key("d"),
        Key("f"),
        Key("g"),
        Key("h"),
        Key("j"),
        Key("k"),
        Key("l"),
        Key(";"),
        Key("'"),
        Key("return", width=1.75),
    ), KeyboardRow(
        Key("shift", modifier=True, width=2.25),
        Key("z"),
        Key("x"),
        Key("c"),
        Key("v"),
        Key("b"),
        Key("n"),
        Key("m"),
        Key(",", code="0x2B"),
        Key(".", code="0x2F"),
        Key("/", code="0x2C"),
        Key("shift", code="rshift", modifier=True, width=2.25),
    ), KeyboardRow(
        Key("fn", modifier=True),
        Key("ctrl", modifier=True),
        Key("alt", modifier=True),
        Key("cmd", modifier=True, width=1.25),
        Key("space", width=5),
        Key("cmd", code="rcmd", modifier=True, width=1.25),
        Key("alt", code="ralt", modifier=True),
        Key("left"),
        Key("up", width=0.5),
        Key("down", width=0.5),
        Key("right")
    )
)

KEY_FN = Key("fn", modifier=True)
KEY_CTRL = Key("ctrl", modifier=True)
KEY_ALT = Key("alt", modifier=True)
KEY_CMD = Key("cmd", modifier=True)


if __name__ == '__main__':
    import argparse
    import sys

    from parser import Shortcut

    if len(sys.argv) == 1:
        print(MAC_KB.render(4, highlight=[KEY_FN, KEY_CTRL, Key("0x2B")]))
        print(MAC_KB.render(8, highlight=[KEY_FN, KEY_CTRL, Key("0x2B")]))
        exit(0)

    parser = argparse.ArgumentParser(description="Visualize keyboard shortcuts")
    parser.add_argument('shortcut', help='keyboard shortcut in skhd notation')
    parser.add_argument('--size', '-s', type=int, default=8, help='size (multiple of 4)')
    args = parser.parse_args()

    print(MAC_KB.render(args.size, highlight=Key.shortcut_list(Shortcut(args.shortcut))))
