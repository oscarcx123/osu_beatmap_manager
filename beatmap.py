import sqlite3
from sqlite3.dbapi2 import connect
# Import the required libraries
from tkinter import *
from tkinter import ttk

class Beatmap():
    def __init__(self) -> None:
        self.create_ui()
        self.connnect_db()
        self.mw.protocol("WM_DELETE_WINDOW", self.on_quitting)
        self.mw.mainloop()
        

    def create_ui(self):
        self.mw = Tk()
        self.mw.geometry("600x350")

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

        self.tree.pack()

        self.query_entry = StringVar()
        self.matches_found = StringVar()
        self.matches_found.set("blablabla")
        self.l1 = Label(self.mw, text="", width=2).pack(side=LEFT)
        self.e1 = Entry(self.mw, textvariable = self.query_entry, width=70).pack(side=LEFT)
        self.l2 = Label(self.mw, text="", width=2).pack(side=LEFT)
        self.b1 = Button(self.mw, text="Search", command=self.exec_query, width=10).pack(side=LEFT)
        self.l3 = Label(self.mw, textvariable = self.matches_found).pack(side=BOTTOM)

    def connnect_db(self):
        self.sql = sqlite3.connect("cache.db")
        self.c = self.sql.cursor()

    def exec_query(self):
        query_1, query_2 = self.parse_query()
        self.c.execute(f"select title_unicode, mapper, difficulty, star from maps where {query_1}", query_2)
        self.tb_values = self.c.fetchall()
        
        self.tree.delete(*self.tree.get_children())
        for i in self.tb_values:
            self.tree.insert('', 'end', text="1", values=i)

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
    
    def close_db(self):
        self.c.close()
        self.sql.close()

    def on_quitting(self):
        self.close_db()
        self.mw.destroy()

beatmap = Beatmap()


