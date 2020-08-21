import requests
import re
from pathlib import Path
import mysql.connector
from music21 import *
from mido import MidiFile
# Verbindung zum Server
mydb = mysql.connector.connect(
        host="localhost",
        user="MusikDBNutzer",
        password="test",
        database="musiksuchmaschine"
)

# bildet eine Liste mit allen Künstlern und ihren IDs
mycursor = mydb.cursor()
sql = "SELECT * FROM kuenstler"
mycursor.execute(sql, )
artistList = mycursor.fetchall()
artistList = str(artistList)

#bildet eine Liste mit allen Musikstücken für Vergleich
#in Zukunft URL vielleicht besser
mycursor = mydb.cursor()
sql = "SELECT * FROM musikstueck"
mycursor.execute(sql, )
musikstuecktList = mycursor.fetchall()
musikstuecktList = str(musikstuecktList)

url = 'http://metal-midi.grahamdowney.com/midi/sepultura/Sepultura-Roots%20bloody%20roots.MID'
r = requests.get(url, allow_redirects=True)
file_name = Path(url).name
file_ext: str = Path(url).suffix
open(file_name, 'wb').write(r.content)
xml = 'xml'
mxl = 'mxl'

if file_ext == 'xml' or file_ext == 'mxl':

    score = converter.parse(file_name)
    varTitle = score.metadata.title
    varArtist = score.metadata.composer
    varSonstiges = score.metadata.all()
    varSonstiges = str(varSonstiges)
    # das Stream Objekt verfügt über Metadaten print nur für den fall von fehlern als kontrolle
    # https://web.mit.edu/music21/doc/moduleReference/moduleMetadata.html?#module-music21.metadata
    # print(score.metadata.title)
    # print(score.metadata.composer)
    # print(score.metadata.date)
    # print(score.metadata.all())
    # print(score.duration)

    # einzelen Variablen mit den entsprechenden Metadaten befüllen


    # secondsMap zeigt alles an, was in Sekdunen angegeben wurde
    # print(score.secondsMap)

    # zeigt alles an, was irgendwie mit dem Tempo zu tun hat
    # print(score.metronomeMarkBoundaries())
    # print(varTitle)

    # trägt Komponisten in DB ein, wenn sie nicht schon da sind
    if varArtist != None and varArtist not in artistList:
        mycursor = mydb.cursor()
        sql = "INSERT INTO kuenstler (ID, Name) VALUES (NULL, %s)"
        val = (varArtist,)
        mycursor.execute(sql, val, )
        mydb.commit()

        # findet ID des Kuenstlers des aktuellen Stückes heraus
    if varTitle != None:
        mycursor = mydb.cursor()
        sql = "SELECT ID FROM kuenstler WHERE Name = %s"
        val = (varArtist,)
        mycursor.execute(sql, val, )
        myresult = mycursor.fetchall()
        # myresult = myresult(0) #hier statt String einfach nur auf Tupel zugreifen
        myresult = str(myresult)  # wandelt den tupel in string
        # der nächste schritt entfernt alle, Kommas und Klammern des String, damit dieser in der DB keine Probleme
        # verursacht
        myresult = myresult.replace(',', '', ).replace('(', '').replace(')', '').replace('[', '').replace(']', '')

        # Trägt Titel in DB ein sofern er nicht schon da ist
        # in zukünftiger Version lieber URL zum Vergleichen nehmen
    if varTitle is not None and varTitle not in musikstuecktList:
        mycursor = mydb.cursor()
        sql = "INSERT INTO musikstueck (ID,Titel,Kuenstler_ID, Sonstiges) VALUES (Null, %s, %s, %s)"
        val = (varTitle, myresult, varSonstiges)
        mycursor.execute(sql, val, )
        mydb.commit()

        # wie regeln wir es, dass Künstler nicht doppelt eingetragen werden?
        # BPM, Länge
else:
    pass
if file_ext == ".mid":
    mid = MidiFile(file_name, clip=True)
    varMisc = []
    varData = ""
    varTitle = ""
    varArtist = ""
    varTempo = ""
    varKey = ""
    varUrl = ""

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
                    vartempo = round(60000000 / vartempo, 0)
                else:
                    varMisc.append(a_string)
                    miscstr = ",".join(varMisc)
            else:
                pass

        if varArtist != None and varArtist not in artistList:
            mycursor = mydb.cursor()
            sql = "INSERT INTO kuenstler (ID, Name) VALUES (NULL, %s)"
            val = (varArtist,)
            mycursor.execute(sql, val, )
            mydb.commit()

        if varTitle != None:
            mycursor = mydb.cursor()
            sql = "SELECT ID FROM kuenstler WHERE Name = %s"
            val = (varArtist,)
            mycursor.execute(sql, val, )
            myresult = mycursor.fetchall()
            # myresult = myresult(0) #hier statt String einfach nur auf Tupel zugreifen
            myresult = str(myresult)  # wandelt den tupel in string
            # der nächste schritt entfernt alle, Kommas und Klammern des String, damit dieser in der DB keine Probleme
            # verursacht
            myresult = myresult.replace(',', '', ).replace('(', '').replace(')', '').replace('[', '').replace(']', '')

        mycursor = mydb.cursor()
    sql = "INSERT INTO musikstueck (ID, Kuenstler_ID, Titel, Tempo, Tonart, URL, Sonstiges) VALUES (NULL, %s, %s, %s, %s, %s, %s)"
    val = (myresult, varTitle, varTempo, varKey, varUrl, miscstr,)
    mycursor.execute(sql, val,)

    mydb.commit()

    # print(mycursor.rowcount, "record inserted.")



