# Modified [Awlexus/python-osu-parser](https://github.com/Awlexus/python-osu-parser)
import re

class BeatmapParser():
    def __init__(self):
        self.beatmap = {}
        self.key_val_reg = re.compile('^([a-zA-Z0-9]+)[ ]*:[ ]*(.+)$')


    # Read a single line, parse when key/value, store when further parsing needed
    # @param  {String|Buffer} line
    def read_line(self, line: str):
        line = line.strip()
        if not line:
            return
        match = self.key_val_reg.match(line)
        if match:
            self.beatmap[match.group(1)] = match.group(2)

    # Parse .osu file
    def parseFile(self, file):
        with open(file, 'r', encoding="utf-8") as file:
            line = file.readline()
            while line:
                if "[Events]" in line:
                    break
                self.read_line(line)
                line = file.readline()