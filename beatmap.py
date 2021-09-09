import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os
from osu2sqlite import GenerateDB
from beatmap_parser import BeatmapParser
from send2trash import send2trash

class Beatmap():
    def __init__(self):
        # If you are using OS other than Windows 10, or if your osu is not in the default directory, then you probably need to change self.osu_folder below
        self.osu_folder = os.path.join(os.getenv('LOCALAPPDATA'), "osu!")
        self.osu_db = os.path.join(self.osu_folder, "osu!.db")
        self.song_folder = os.path.join(self.osu_folder, "Songs")
        self.tb_values = []

    def launch(self):
        self.create_ui()
        if not self.connnect_db():
            return
        self.mw.protocol("WM_DELETE_WINDOW", self.on_quitting)
        self.mw.mainloop()
        

    def create_ui(self):
        self.mw = Tk()
        self.mw.geometry("600x320")
        self.mw.title("Osu Beatmap Manager by oscarcx123")

        self.f1 = Frame(self.mw)
        self.f2 = Frame(self.mw)
        self.f3 = Frame(self.mw)

        # Add a Treeview widget
        self.tree = ttk.Treeview(self.mw, column=("title_unicode", "mapper", "difficulty", "star_mania"), show='headings', height=10)
        self.tree.column("#1", width=200)
        self.tree.heading("#1", text="Title")
        self.tree.column("#2", width=100)
        self.tree.heading("#2", text="Mapper")
        self.tree.column("#3", width=200)
        self.tree.heading("#3", text="Difficulty")
        self.tree.column("#4", width=50)
        self.tree.heading("#4", text="SR")

        # Add a Vertical Scrollbar
        self.verscrlbar = ttk.Scrollbar(self.mw, orient ="vertical", command = self.tree.yview)
        self.verscrlbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=self.verscrlbar.set)

        self.tree.pack(anchor=W, padx=10)

        self.query_entry = StringVar()
        self.matches_found = StringVar()
        self.matches_found.set("Search just like you do in osu!")
        self.e1 = Entry(self.f1, textvariable = self.query_entry, width=60)
        self.e1.pack(side=LEFT)
        self.l1 = Label(self.f1, text="", width=2)
        self.l1.pack(side=LEFT)
        self.b1 = Button(self.f1, text="Search", command=self.exec_query, width=10)
        self.b1.pack(side=LEFT)
        self.b2 = Button(self.f1, text="Delete", command=self.delete_files, width=10)
        self.b2.pack(side=LEFT, padx=10)
        self.l2 = Label(self.f2, textvariable = self.matches_found)
        self.l2.pack(side=LEFT)
        self.p1 = ttk.Progressbar(self.f3, orient=HORIZONTAL, length=550, mode='determinate')
        self.p1.pack()

        self.f1.pack(anchor=W, padx=10)
        self.f2.pack(anchor=W, padx=10)
        self.f3.pack(anchor=W, padx=10)

    def connnect_db(self):
        if not os.path.exists("cache.db"):
            if not os.path.exists(self.osu_db):
                print(f"Failed to find osu!.db in {self.osu_folder}")
                print(f"If osu is not installed in the default path, you will need to edit <osu_folder> manually at the beginning of this file")
                return False
            else:
                print("Generating cache.db")
                generate_db = GenerateDB()
                generate_db.generate(self.osu_db)
                print("cache.db done!")
        self.sql = sqlite3.connect("cache.db")
        self.c = self.sql.cursor()
        return True

    def exec_query(self):
        self.query_1, self.query_2 = self.parse_query()
        self.c.execute(f"select title_unicode, mapper, difficulty, star, folder_name, map_file from maps where {self.query_1}", self.query_2)
        self.tb_values = self.c.fetchall()
        
        self.tree.delete(*self.tree.get_children())
        for i in self.tb_values:
            show_data = i[0:4]
            self.tree.insert('', 'end', text="1", values=show_data)

        if len(self.tb_values) == 1:
            self.matches_found.set("1 match found!")
        self.matches_found.set(f"{len(self.tb_values)} matches found!")

    # mode=m, key=7, k-on
    def parse_query(self):
        cond = []
        query = []
        mode = {
            "o": 0,
            "t": 1,
            "c": 2,
            "m": 3
        }
        status = {
            "unknown": 0,
            "u": 0,
            "notsubmitted": 1,
            "n": 1,
            "pending": 2,
            "p": 2,
            "ranked": 4,
            "r": 4,
            "approved": 5,
            "a": 5,
            "qualified": 6,
            "q": 6,
            "loved": 7,
            "l": 7,
        }
        operators = ["!=", "<=", ">=", "=", "<", ">"]
        s = self.query_entry.get()
        lst = s.split(",")
        for idx in range(len(lst)):
            lst[idx] = lst[idx].lstrip()
            is_text = True
            for op in operators:
                if op in lst[idx]:
                    tmp = lst[idx].split(op)
                    tmp.insert(1, op)
                    cond.append(tmp)
                    is_text = False
                    break
            if is_text:
                cond.append([lst[idx]])

        for idx in range(len(cond)):
            if cond[idx][0] == "mode":
                if cond[idx][2] in mode:
                    query.append([f"gameplay_mode{cond[idx][1]}?", f"{mode[cond[idx][2]]}"])
            
            elif cond[idx][0] == "artist":
                query.append([f"artist LIKE ?", f"%{cond[idx][2]}%"])
            elif cond[idx][0] == "creator":
                query.append([f"mapper LIKE ?", f"%{cond[idx][2]}%"])
            elif cond[idx][0] == "ar":
                query.append([f"approach_rate{cond[idx][1]}?", f"{cond[idx][2]}"])
            elif cond[idx][0] == "key" or cond[idx][0] == "cs":
                query.append([f"circle_size{cond[idx][1]}?", f"{cond[idx][2]}"])
            elif cond[idx][0] == "od":
                query.append([f"overall_difficulty{cond[idx][1]} ?", f"{cond[idx][2]}"])
            elif cond[idx][0] == "hp":
                query.append([f"hp_drain{cond[idx][1]}?", f"{cond[idx][2]}"])
            elif cond[idx][0] == "star" or cond[idx][0] == "stars":
                query.append([f"star{cond[idx][1]}?", f"{cond[idx][2]}"])
            elif cond[idx][0] == "hp":
                query.append([f"hp_drain{cond[idx][1]}?", f"{cond[idx][2]}"])
            elif cond[idx][0] == "bpm":
                query.append([f"bpm{cond[idx][1]}?", f"{cond[idx][2]}"])
            elif cond[idx][0] == "length":
                query.append([f"total_time{cond[idx][1]}?", f"{int(cond[idx][2])*1000}"])
            elif cond[idx][0] == "drain":
                query.append([f"drain_time{cond[idx][1]}?", f"{cond[idx][2]}"])
            elif cond[idx][0] == "status":
                if cond[idx][2] in status:
                    query.append([f"ranked_status=?", f"{status[cond[idx][2]]}"])
            elif len(cond[idx]) == 1:
                text_lst = cond[idx][0]
                text_lst = text_lst.split(" ")
                for idx in range(len(text_lst)):
                    query.append([f"text_search LIKE ?", f"%{text_lst[idx]}%"])
            else:
                print(f"Warning: Unknown syntax ({cond[idx]})")
                
        
        query_1 = [x[0] for x in query]
        query_2 = [x[1] for x in query]
        print(query)

        return " AND ".join(query_1), query_2
    
    def delete_files(self):
        self.p1['value'] = 0
        self.p1.update()

        if len(self.tb_values) == 0:
            self.matches_found.set("You need to search first! Example: mode=m, key=7")
            return
        
        if messagebox.askyesno("Final Confirmation", f"Do you really want to delete {len(self.tb_values)} maps?"):
            parser = BeatmapParser()
            for idx in range(len(self.tb_values)):
                s = self.tb_values[idx]
                map_folder = os.path.join(self.song_folder, s[4])
                osu_file = os.path.join(map_folder, s[5])
                
                # if it's a song pack (Multiple audio files)
                try:
                    if len([x for x in os.listdir(map_folder) if x.endswith(".mp3")]) > 1:
                        parser.parseFile(osu_file)
                        audio_file = parser.beatmap["AudioFilename"]
                        delete_audio = True
                        other_osu_files = [x for x in os.listdir(map_folder) if x.endswith(".osu") and x != s[5]]
                        
                        # loop through all the osu files to make sure that the audio is solely used by the current osu file.
                        for item in other_osu_files:
                            parser.parseFile(os.path.join(map_folder, item))
                            if audio_file == parser.beatmap["AudioFilename"]:
                                delete_audio = False
                                break
                        if delete_audio:
                            send2trash(os.path.join(map_folder, audio_file))
                except:
                    pass

                send2trash(osu_file)
                
                try:
                    if len([x for x in os.listdir(map_folder) if x.endswith(".osu")]) == 0:
                        send2trash(map_folder)
                except:
                    print(f"Something wrong with {map_folder}")
                self.p1['value'] = 100 * (idx+1) / len(self.tb_values)
                self.p1.update()
            
            # delete corresponding entries in cache.db
            self.c.execute(f"delete from maps where {self.query_1}", self.query_2)
            self.tb_values = []
            
            # clean treeview
            self.tree.delete(*self.tree.get_children())
        
    
    def close_db(self):
        self.c.close()
        self.sql.close()

    def on_quitting(self):
        self.close_db()
        self.mw.destroy()

beatmap = Beatmap()
beatmap.launch()
