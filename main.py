import os
import re
import json
import shutil
from send2trash import send2trash


# Modified [Awlexus/python-osu-parser](https://github.com/Awlexus/python-osu-parser)
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


class BeatmapMgr():
    def __init__(self):
        self.song_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'osu!', 'Songs')
        self.osu_info = []
        self.selected_info = []


    def generate_info(self):
        parser = BeatmapParser()
        # Get all song folders
        folder_list = os.listdir(self.song_dir)

        self.osu_info = []
        folder_list_len = len(folder_list)

        for idx in range(folder_list_len):
            folder = folder_list[idx]
            print(f"Progress: {idx+1} / {folder_list_len}")
            folder_path = os.path.join(self.song_dir, folder)
            # Get all .osu files in a folder
            osu_file = [x for x in os.listdir(folder_path) if x.endswith(".osu")]
            for item in osu_file:
                self.osu_info.append({})
                osu_file_path = os.path.join(folder_path, item)
                parser.parseFile(osu_file_path)
                self.osu_info[-1]["path"] = osu_file_path
                self.osu_info[-1]["folder_path"] = folder_path
                self.osu_info[-1]["mode"] =  parser.beatmap["Mode"]
                self.osu_info[-1]["title"] = parser.beatmap["Title"]
                self.osu_info[-1]["artist"] = parser.beatmap["Artist"]
                self.osu_info[-1]["creator"] = parser.beatmap["Creator"]
                self.osu_info[-1]["version"] = parser.beatmap["Version"]
                if "Source" in parser.beatmap:
                    self.osu_info[-1]["source"] = parser.beatmap["Source"]
                else:
                    self.osu_info[-1]["source"] = "None"
                self.osu_info[-1]["cs"] = parser.beatmap["CircleSize"]
                if "Tags" in parser.beatmap:
                    self.osu_info[-1]["tags"] = parser.beatmap["Tags"]
                else:
                    self.osu_info[-1]["tags"] = "None"
                self.osu_info[-1]["search_text"] = " ".join([
                    self.osu_info[-1]["title"], 
                    self.osu_info[-1]["artist"],
                    self.osu_info[-1]["creator"],
                    self.osu_info[-1]["source"],
                    self.osu_info[-1]["tags"],
                    self.osu_info[-1]["version"]
                ])


        with open("osu_info.json","w") as f:
            json.dump(self.osu_info, f)

    def read_info(self):
        json_path = os.path.join(os.getcwd(), "osu_info.json")
        try:
            with open(json_path,"r") as f:
                self.osu_info = json.load(f)
        except:
            print("No json file found...")

    def select_info(self, params):
        self.selected_info = []
        if self.osu_info == []:
            print("No result!")
            return
        osu_info_len = len(self.osu_info)
        for idx in range(osu_info_len):
            song = self.osu_info[idx]
            print(f"Progress: {idx+1} / {osu_info_len}")
            cnt = 0
            for req in params:
                key = req[0]
                val = req[1]
                if key == "search_text":
                    if val.lower() in song[key].lower():
                        cnt += 1
                elif song[key] == val:
                    cnt += 1
            if cnt == len(params):
                self.selected_info.append(song)
        print(f"Found {len(self.selected_info)} map(s)!")

    def list_selected_info(self):
        for idx in range(len(self.selected_info)):
            print(f"#{idx+1} {self.selected_info[idx]['artist']} - {self.selected_info[idx]['title']} ({self.selected_info[idx]['creator']}) [{self.selected_info[idx]['version']}]")

    def delete_selected_info(self):
        selected_info_len = len(self.selected_info)
        for idx in range(selected_info_len):
            print(f"Progress: {idx+1} / {selected_info_len}")
            send2trash(self.selected_info[idx]['path'])
            folder_path = self.selected_info[idx]['folder_path']
            try:
                if not [x for x in os.listdir(folder_path) if x.endswith(".osu")]:
                    try:
                        send2trash(folder_path)
                    except OSError as e:
                        print(e)
                        print("Will try to ignore the error and continue...")
            except FileNotFoundError as e:
                print(e)
                print("The song folder has been changed. Please use \"generate\" to update the json db")
                break
        
        # flush the info json
        self.generate_info()

    # Remove sv from selected song files
    def remove_sv(self):
        for idx in range(len(self.selected_info)):
            print(f"#{idx+1} {self.selected_info[idx]['artist']} - {self.selected_info[idx]['title']} ({self.selected_info[idx]['creator']}) [{self.selected_info[idx]['version']}]")
            with open(self.selected_info[idx]['path'], "r") as f:
                lines = f.readlines()
            with open(self.selected_info[idx]['path'], "w") as f:
                idx = 0
                found = False
                init_timing_line = False
                for line in lines:
                    if line.strip("\n") == "[TimingPoints]":
                        found = True
                        init_timing_line = True
                        f.write(line)
                        continue
                    if found:
                        if init_timing_line:
                            init_timing_line = False
                            f.write(line)
                            continue
                        if line.strip("\n") != "":
                            continue
                        else:
                            found = False
                            f.write(line)
                            continue
                    f.write(line)


print("OsuBeatmapMgr V1.0")
print("Use \"help\" for usage instruction")
Mgr = BeatmapMgr()
Mgr.read_info()
while True:
    cmd = input(">>> ")
    if cmd == "help":
        handbook = {
            "generate": "generate json db from osu",
            "select": "apply filter to json db",
            "select usage": "select param1=aaa,param2=bbb",
            "select example": "select mode=m,key=7,text=lvl",
            "list": "show all selected beatmaps",
            "delete": "remove all selected beatmaps",
            "remove_sv": "remove all SV from selected beatmaps"
        }
        for idx in handbook:
            print(f"{idx} - {handbook[idx]}")
    elif cmd == "generate":
        Mgr.generate_info()
    elif cmd.split(" ")[0] == "select":
        params = []
        if cmd == "select":
            print("No param detected...")
            break
        cmd = cmd.replace("select ","")
        cmd_list = cmd.split(",")
        for item in cmd_list:
            args = item.split("=")
            params.append([])
            if args[0] == "mode":
                if args[1] == "0" or args[1] == "s":
                    params[-1] = ["mode", "0"]
                elif args[1] == "1" or args[1] == "t":
                    params[-1] = ["mode", "1"]
                elif args[1] == "2" or args[1] == "c":
                    params[-1] = ["mode", "2"]
                elif args[1] == "3" or args[1] == "m":
                    params[-1] = ["mode", "3"]
            elif args[0] == "cs" or args[0] == "key":
                params[-1] = ["cs", args[1]]
            elif args[0] == "text":
                params[-1] = ["search_text", args[1]]
        Mgr.select_info(params)
    elif cmd == "list":
        Mgr.list_selected_info()
    elif cmd == "delete":
        Mgr.delete_selected_info()
    elif cmd == "remove_sv":
        Mgr.remove_sv()
    elif cmd == "exit":
        break
    else:
        print(f"{cmd} is not a valid command!")
