import re
from mido import MidiFile
import mysql.connector

mydb = mysql.connector.connect (
    host="localhost",
    user="metadb",
    password="metadata",
    database="metadata"
)

files = ["AUD_AP0164.mid", "AUD_AP1435H.mid", "AUD_CT0027.mid", "AUD_DS1189.mid"]
for file in files:
    mid = MidiFile(file, clip=True)
    varmisc = []
    vardata = ""
    vartitle = ""
    varartist = ""
    vartempo = ""
    varkey = ""
    varurl = ""

    for track in mid.tracks:
        for msg in mid.tracks[0]:
            msg = str(msg)
            x = re.search("<meta message.*time=0>", msg)
            remove_characters = ["<", ">", "meta message", "time=0", "'"]
            if x:
                a_string = str(x.string)
                for character in remove_characters:
                    a_string = a_string.replace(character, "")
                if "track_name" in msg:
                    vartitle = a_string.replace("track_name name=", "")
                if "key_signature" in msg:
                    varkey = a_string.replace("key_signature key=", "")
                if "set_tempo" in msg:
                    vartempo = a_string.replace("set_tempo tempo=", "")
                    vartempo = int(vartempo)
                    vartempo = round(60000000/vartempo, 0)
                else:
                    varmisc.append(a_string)
                    miscstr = ",".join(varmisc)
            else:
                pass

    mycursor = mydb.cursor()

    sql = "INSERT INTO data (Dateiname, Titel, Interpret, Tempo, Tonart, URL, Sonstiges) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (vardata, vartitle, varartist, vartempo, varkey, varurl, miscstr)
    mycursor.execute(sql, val)

    mydb.commit()

    #print(mycursor.rowcount, "record inserted.")