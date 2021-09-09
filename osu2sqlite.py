# https://github.com/jaasonw/osu-db-tools
# modified to fit this project
import buffer
import sqlite3

class GenerateDB():
    def __init__(self) -> None:
        pass

    def generate(self, osu_db):
        self.create_db(osu_db)

    def create_db(self, filename):
        sql = sqlite3.connect("cache.db")
        c = sql.cursor()
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='maps' ''')
        if c.fetchone()[0] == 1:
            sql.execute("DROP TABLE maps")
        sql.execute("""
            CREATE TABLE maps (
                artist TEXT,
                artist_unicode TEXT,
                title TEXT,
                title_unicode TEXT,
                mapper TEXT,
                difficulty TEXT,
                audio_file TEXT,
                md5_hash TEXT,
                map_file TEXT,
                ranked_status INTEGER,
                num_hitcircles INTEGER,
                num_sliders INTEGER,
                num_spinners INTEGER,
                last_modified INTEGER,
                approach_rate NUMERIC,
                circle_size NUMERIC,
                hp_drain NUMERIC,
                overall_difficulty NUMERIC,
                slider_velocity NUMERIC,
                star FLOAT,
                star_DT FLOAT,
                star_HT FLOAT,
                drain_time INTEGER,
                total_time INTEGER,
                preview_time INTEGER,
                bpm FLOAT,
                beatmap_id INTEGER,
                beatmap_set_id INTEGER,
                thread_id INTEGER,
                grade_stadard INTEGER,
                grade_taiko INTEGER,
                grade_ctb INTEGER,
                grade_mania INTEGER,
                local_offset INTEGER,
                stack_leniency NUMERIC,
                gameplay_mode INTEGER,
                song_source TEXT,
                song_tags TEXT,
                online_offset INTEGER,
                font TEXT,
                is_unplayed INTEGER,
                last_played INTEGER,
                is_osz2 INTEGER,
                folder_name TEXT,
                last_checked INTEGER,
                ignore_sounds INTEGER,
                ignore_skin INTEGER,
                disable_storyboard INTEGER,
                disable_video INTEGER,
                visual_override INTEGER,
                last_modified2 INTEGER,
                mania_speed INTEGER,
                text_search TEXT
            );
        """)
        with open(filename, "rb") as db:
            version = buffer.read_uint(db)
            folder_count = buffer.read_uint(db)
            account_unlocked = buffer.read_bool(db)
            # skip this datetime shit for now (8 bytes)
            buffer.read_uint(db)
            buffer.read_uint(db)
            name = buffer.read_string(db)
            num_beatmaps = buffer.read_uint(db)

            for _ in range(num_beatmaps):
                artist = buffer.read_string(db)
                artist_unicode = buffer.read_string(db)
                song_title = buffer.read_string(db)
                song_title_unicode = buffer.read_string(db)
                mapper = buffer.read_string(db)
                difficulty = buffer.read_string(db)
                audio_file = buffer.read_string(db)
                md5_hash = buffer.read_string(db)
                map_file = buffer.read_string(db)
                ranked_status = buffer.read_ubyte(db)
                num_hitcircles = buffer.read_ushort(db)
                num_sliders = buffer.read_ushort(db)
                num_spinners = buffer.read_ushort(db)
                last_modified = buffer.read_ulong(db)
                approach_rate = buffer.read_float(db)
                circle_size = buffer.read_float(db)
                hp_drain = buffer.read_float(db)
                overall_difficulty = buffer.read_float(db)
                slider_velocity = buffer.read_double(db)

                star_ratings = []
                i = buffer.read_uint(db)
                for _ in range(i):
                    star_ratings.append(buffer.read_int_double(db))
                if len(star_ratings):
                    star = round(star_ratings[0][1], 2)
                    star_DT = round(star_ratings[1][1], 2)
                    star_HT = round(star_ratings[2][1], 2)

                star_ratings = []
                i = buffer.read_uint(db)
                for _ in range(i):
                    star_ratings.append(buffer.read_int_double(db))
                if len(star_ratings):
                    star = round(star_ratings[0][1], 2)
                    star_DT = round(star_ratings[1][1], 2)
                    star_HT = round(star_ratings[2][1], 2)

                star_ratings = []
                i = buffer.read_uint(db)
                for _ in range(i):
                    star_ratings.append(buffer.read_int_double(db))
                if len(star_ratings):
                    star = round(star_ratings[0][1], 2)
                    star_DT = round(star_ratings[1][1], 2)
                    star_HT = round(star_ratings[2][1], 2)

                star_ratings = []
                i = buffer.read_uint(db)
                for _ in range(i):
                    star_ratings.append(buffer.read_int_double(db))
                if len(star_ratings):
                    star = round(star_ratings[0][1], 2)
                    star_DT = round(star_ratings[1][1], 2)
                    star_HT = round(star_ratings[2][1], 2)

                drain_time = buffer.read_uint(db)
                total_time = buffer.read_uint(db)
                preview_time = buffer.read_uint(db)
                # skip timing points
                # i = buffer.read_uint(db)
                timing = []
                for _ in range(buffer.read_uint(db)):
                    timing.append(buffer.read_timing_point(db))
                    if len(timing) >= 1:
                        bpm = round(timing[0][0], 2)
                    else:
                        bpm = 0
                beatmap_id = buffer.read_uint(db)
                beatmap_set_id = buffer.read_uint(db)
                thread_id = buffer.read_uint(db)
                grade_standard = buffer.read_ubyte(db)
                grade_taiko = buffer.read_ubyte(db)
                grade_ctb = buffer.read_ubyte(db)
                grade_mania = buffer.read_ubyte(db)
                local_offset = buffer.read_ushort(db)
                stack_leniency = buffer.read_float(db)
                gameplay_mode = buffer.read_ubyte(db)
                song_source = buffer.read_string(db)
                song_tags = buffer.read_string(db)
                online_offset = buffer.read_ushort(db)
                title_font = buffer.read_string(db)
                is_unplayed = buffer.read_bool(db)
                last_played = buffer.read_ulong(db)
                is_osz2 = buffer.read_bool(db)
                folder_name = buffer.read_string(db)
                last_checked = buffer.read_ulong(db)
                ignore_sounds = buffer.read_bool(db)
                ignore_skin = buffer.read_bool(db)
                disable_storyboard = buffer.read_bool(db)
                disable_video = buffer.read_bool(db)
                visual_override = buffer.read_bool(db)
                last_modified2 = buffer.read_uint(db)
                scroll_speed = buffer.read_ubyte(db)
                text_search = " ".join([
                    artist,
                    artist_unicode,
                    song_title,
                    song_title_unicode,
                    mapper,
                    difficulty,
                    song_source,
                    song_tags
                ])
                
                sql.execute(
                    "INSERT INTO maps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (artist,artist_unicode,song_title,song_title_unicode,mapper,difficulty,audio_file,md5_hash,map_file,ranked_status,num_hitcircles,num_sliders,num_spinners,last_modified,approach_rate,circle_size,hp_drain,overall_difficulty,slider_velocity,star,star_DT,star_HT,drain_time,total_time,preview_time,bpm,beatmap_id,beatmap_set_id,thread_id,grade_standard,grade_taiko,grade_ctb,grade_mania,local_offset,stack_leniency,gameplay_mode,song_source,song_tags,online_offset,title_font,is_unplayed,last_played,is_osz2,folder_name,last_checked,ignore_sounds,ignore_skin,disable_storyboard,disable_video,visual_override,last_modified2,scroll_speed,text_search)
                )
            sql.commit()
            sql.close()

if __name__ == "__main__":
    osu_db = "osu!.db"
    generate_db = GenerateDB()
    generate_db.generate(osu_db)