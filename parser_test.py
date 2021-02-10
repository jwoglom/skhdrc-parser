import unittest
import tempfile
import pprint


from parser import Shortcut, Parser


class TestShortcut(unittest.TestCase):
    def test_parse(self):
        tests = {
            "cmd + ctrl + alt - 1":
                [None, {"cmd", "ctrl", "alt"}, "1"],
            "cmd + ctrl + alt-1":
                [None, {"cmd", "ctrl", "alt"}, "1"],
            "cmd+ctrl  +   alt-1":
                [None, {"cmd", "ctrl", "alt"}, "1"],
            "cmd + ctrl + alt - 0x2C":
                [None, {"cmd", "ctrl", "alt"}, "0x2C"],
            "cmd + ctrl + ralt + lalt - 0x2B":
                [None, {"cmd", "ctrl", "ralt", "lalt"}, "0x2B"],
            ":: default":
                ["default", [], ""],
            "resize   <  up":
                ["resize", [], "up"],
            "resize   <  shift - up":
                ["resize", {"shift"}, "up"]
        }

        for inp, res in tests.items():
            s = Shortcut(inp)
            mode, operators, key = res
            self.assertEqual(s.mode, mode, "mode for %s should be: %s is: %s" % (inp, mode, s.mode))
            self.assertEqual(set(s.operators), set(operators), "operators for %s should be: %s is: %s" % (inp, operators, s.operators))
            self.assertEqual(s.key, key, "key for %s should be: %s is: %s" % (inp, key, s.key))

class TestParser(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.file.close()

    def test_basic(self):
        self.file.write(b"""
# close window
shift + cmd + ctrl + alt - q : yabai -m window --close

# restart skhd.
shift + cmd + ctrl + alt - r : bash -c '$WMSCRIPTS/n.sh "yabai" "reloading skhd" && skhd --reload'
""")
        self.file.flush()

        p = Parser(self.file.name)
        self.assertEqual(p.parse(),
            ({
                Shortcut("shift+cmd+ctrl+alt-q"): "close window",
                Shortcut("shift+cmd+ctrl+alt-r"): "restart skhd."
            }, {
                Shortcut("shift+cmd+ctrl+alt-q"): "yabai -m window --close",
                Shortcut("shift+cmd+ctrl+alt-r"): "bash -c '$WMSCRIPTS/n.sh \"yabai\" \"reloading skhd\" && skhd --reload'"
            }))

    def test_multiline(self):
        self.file.write(b"""
# move windows. for left and right, if the window can't move then move it to the next side of the display in that direction and focus it
# specify ralt explicitly because lalt is used for other shortcuts
shift + cmd + ctrl + ralt - left : yabai -m window --warp west || yabai -m window --swap west || (yabai -m window --display west && yabai -m display --focus west)

# Create space on the active display and jump to it
cmd + ctrl + alt - c : yabai -m space --create; \\
                       id="$(yabai -m query --spaces --display | jq 'map(select(."native-fullscreen" == 0))[-1].index')"; \\
                       yabai -m space --focus $id; \\
                       $WMSCRIPTS/notify_bar.sh

""")
        self.file.flush()

        p = Parser(self.file.name)
        pprint.pprint(p.parse())

        self.assertEqual(p.parse(),
            ({
                Shortcut("shift + cmd + ctrl + ralt - left"): "move windows. for left and right, if the window can't move then move it to the next side of the display in that direction and focus it\nspecify ralt explicitly because lalt is used for other shortcuts",
                Shortcut("cmd + ctrl + alt - c"): "Create space on the active display and jump to it"
            }, {
                Shortcut("shift + cmd + ctrl + ralt - left"): "yabai -m window --warp west || yabai -m window --swap west || (yabai -m window --display west && yabai -m display --focus west)",
                Shortcut("cmd + ctrl + alt - c"): "yabai -m space --create; \\\nid=\"$(yabai -m query --spaces --display | jq 'map(select(.\"native-fullscreen\" == 0))[-1].index')\"; \\\nyabai -m space --focus $id; \\\n$WMSCRIPTS/notify_bar.sh"
            }))

    def test_modeswitch(self):
        self.file.write(b"""
:: default : $WMSCRIPTS/n.sh "yabai" "default mode"
:: resize  : $WMSCRIPTS/n.sh "yabai" "resize mode"
default  <  cmd + ctrl + alt - r         ; resize
resize   <  escape         ; default
resize   <  up             : yabai -m window --resize top:0:-100 ; yabai -m window --resize bottom:0:-100
resize   <  shift - up     : yabai -m window --resize top:0:-20 ; yabai -m window --resize bottom:0:-20
""")
        self.file.flush()

        p = Parser(self.file.name)
        pprint.pprint(p.parse())

        self.assertEqual(p.parse()[1],
            {
                Shortcut(":: default"): "$WMSCRIPTS/n.sh \"yabai\" \"default mode\"",
                Shortcut(":: resize"): "$WMSCRIPTS/n.sh \"yabai\" \"resize mode\"",
                Shortcut("default  <  cmd + ctrl + alt - r"): "modeswitch resize",
                Shortcut("resize  <  escape"): "modeswitch default",
                Shortcut("resize  <  up"): "yabai -m window --resize top:0:-100 ; yabai -m window --resize bottom:0:-100",
                Shortcut("resize  <  shift - up"): "yabai -m window --resize top:0:-20 ; yabai -m window --resize bottom:0:-20",

            })

if __name__ == '__main__':
    unittest.main()