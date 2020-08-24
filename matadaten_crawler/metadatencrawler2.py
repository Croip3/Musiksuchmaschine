import requests
import re
from pathlib import Path
import mysql.connector
from music21 import *
from mido import MidiFile
import magic
# zur Installation von magic siehe hier: https://pypi.org/project/python-magic/
from xml.etree import ElementTree as ET
import time
start = time.time()

mydb = mysql.connector.connect(
    host="localhost",
    user="MusikDBNutzer",
    password="test",
    database="musiksuchmaschine"
)

#bildet eine Liste mit allen Künstlern und ihren IDs
mycursor = mydb.cursor()
sql = "SELECT * FROM kuenstler"
mycursor.execute(sql, )
artistList = mycursor.fetchall()
artistList = str(artistList)

# bildet eine Liste mit allen Musikstücken
mycursor = mydb.cursor()
sql = "SELECT * FROM musikstueck"
mycursor.execute(sql, )
musikstuecktList = mycursor.fetchall()
musikstuecktList = str(musikstuecktList)

url = 'https://www.mididb.com/midi-download/AUD_ST6355.mid'
# MXL BEISPIEL http://www1.cpdl.org/wiki/images/a/a5/Farewell%2C_my_joy.mxl
# xml BEISPIEL https://hymnary.org/media/fetch/100034
# midi Beispiel https://www.midiworld.com/download/3972
# nicht musikalisches xml beispiel https://www.w3schools.com/xml/simple.xml
r = requests.get(url, allow_redirects=True)
file_name = Path(url).name
file_ext: str = Path(url).suffix
open(file_name, 'wb').write(r.content)
if file_ext == '':
    file_ext = str(magic.from_file(file_name, mime=True))
    file_ext = Path(file_ext).name
    file_ext = file_ext[:4]
    file_name = str(file_name) + '.' + file_ext  # benennt Datei mit richtiger Endung
else:
    pass

open(file_name, 'wb').write(r.content)

if file_ext == 'xml' or file_ext == '.xml' or file_ext == '.mxl' or file_ext == 'mxl':
    et = ET.parse(file_name)
    root = et.getroot()
    root = root.tag
    if root != 'score-partwise':
        print('Dieses XML ist kein musicXML')
        exit()
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
    if varArtist is not None and varArtist not in artistList:
        mycursor = mydb.cursor()
        sql = "INSERT INTO kuenstler (ID, Name) VALUES (NULL, %s)"
        val = (varArtist,)
        mycursor.execute(sql, val, )
        mydb.commit()

        # findet ID des Kuenstlers des aktuellen Stückes heraus
    if varTitle is not None:
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
if file_ext == '.mid' or file_ext == 'midi':
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
                    varTitle = a_string.replace("track_name name=", "")
                if "key_signature" in msg:
                    varKey = a_string.replace("key_signature key=", "")
                if "set_tempo" in msg:
                    varTempo = a_string.replace("set_tempo tempo=", "")
                    varTempo = int(varTempo)
                    varTempo = round(60000000 / varTempo, 0)
                else:
                    varMisc.append(a_string)
                    miscstr = ",".join(varMisc)
            else:
                pass

        if varArtist is not None and varArtist not in artistList:
            mycursor = mydb.cursor()
            sql = "INSERT INTO kuenstler (ID, Name) VALUES (NULL, %s)"
            val = (varArtist,)
            mycursor.execute(sql, val, )
            mydb.commit()

        if varTitle is not None:
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
    mycursor.execute(sql, val, )

    mydb.commit()

    # print(mycursor.rowcount, "record inserted.")
else:
    pass
end = time.time()
print(f"Runtime is: {end - start}")
