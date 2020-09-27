import requests
from bs4 import BeautifulSoup
import re
import threading
import queue
import time
import mysql.connector
import urllib.parse
import datetime

from pathlib import Path
import pathlib
from music21 import *
from mido import MidiFile
import magic
import numpy as np
from xml.etree import ElementTree as ET




dbconfig = { "host": "localhost",
        "user": "root",
        "password" : "3X2SDuKU8v5",
        # "password": "",
        "database": "musiksuchmaschine"}
mydb = mysql.connector.connect(
        host = dbconfig["host"],
        user = dbconfig["user"],
        password = dbconfig["password"],
        database = dbconfig["database"],
    )


class CrawlThread(threading.Thread):
    def __init__(self, url, title):
        threading.Thread.__init__(self)
        self.url = url
        self.title = title

    def run(self):
        while True:
            if not q.empty():
                self.url = q.get()
                crawler(self.url)
                global last_amount_crawled
                global last_amount_links
                global database_push_amount
                global last_amount_artist
                global last_amount_instruments
                print(f"THREAD {self.title} going for {self.url}")
                with queueLock:
                    d = len(hrefList) - last_amount_crawled
                    if d > database_push_amount:
                        print("DATABASE PUSH:\n")
                        global mydb
                        if not mydb.is_connected():
                            print("MUST CONNECT FIRST")
                            mydb = mysql.connector.connect(
                                host=dbconfig["host"],
                                user=dbconfig["user"],
                                password=dbconfig["password"],
                                database=dbconfig["database"],
                            )
                        # BISHER GECRAWLTE URLs
                        records = []
                        for k in range(last_amount_crawled, len(hrefList)):
                            records.append(hrefList[k].get_str())
                        mycursor = mydb.cursor()
                        sql = "INSERT INTO crawled_urls (url, last, ParentId) VALUES (%s, %s, %s)"
                        mycursor.executemany(sql, records)

                        # INSTRUMENTE
                        records = []
                        for k in range(last_amount_instruments, len(instrumentList)):
                            records.append(instrumentList[k].get_str())
                        mycursor2 = mydb.cursor()
                        sql2 = "INSERT INTO instrument VALUES (%s, %s)"
                        mycursor2.executemany(sql2, records)

                        # ALLE GEFUNDENEN MUSIKSTÜCKE
                        records = []
                        cross_records = []
                        for k in range(last_amount_links, len(linkList)):
                            for instr in linkList[k].instruments:
                                cross_records.append((linkList[k].id, instr.id, instr.amount,))
                            records.append(linkList[k].get_str())
                        mycursor2 = mydb.cursor()
                        sql2 = "INSERT INTO musikstueck (Tempo, Genre, Uploaddatum, Laenge, Jahr, Tonart, Epoche, Titel, Url, Kuenstler_ID, Sonstiges) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        mycursor2.executemany(sql2, records)
                        print(f"{mycursor2.rowcount} new music files pushed!")

                        # BEINHALTET
                        mycursor = mydb.cursor()
                        sql = "INSERT INTO beinhaltet VALUES (%s, %s, %s)"
                        mycursor.executemany(sql, cross_records)

                        # KUENSTLER
                        records = []
                        for k in range(last_amount_artist, len(artistList)):
                            records.append(artistList[k].get_str())
                        mycursor2 = mydb.cursor()
                        sql2 = "INSERT INTO kuenstler VALUES (%s, %s)"
                        mycursor2.executemany(sql2, records)

                        # ERRORS
                        records = []
                        for k in range(0, len(errors)):
                            records.append(errors[k].get_str())
                        mycursor2 = mydb.cursor()
                        sql2 = "INSERT INTO error (zeit, nachricht, url) VALUES (%s, %s, %s)"
                        mycursor2.executemany(sql2, records)
                        errors.clear()



                        mydb.commit()

                        last_amount_crawled = len(hrefList)
                        last_amount_links = len(linkList)
                        last_amount_artist = len(artistList)
                        last_amount_instruments = len(instrumentList)
                q.task_done()


class Kuenstler():
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def get_str(self):
        return self.id, self.name

    def set_id(self, id):
        self.id = id

    def find_artist_id(self):
        global artistList
        for artist in artistList:
            if self == artist:
                self.name = artist.name
                self.id = artist.id
                return False
        if len(artistList) != 0:
            self.id = artistList[len(artistList) - 1].id + 1
        else:
            self.id = 1
        return True


class Instrument:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.amount = 1

    def __eq__(self, other):
        return self.name == other.name

    def get_str(self):
        return self.id, self.name

    def inc_amount(self):
        self.amount = self.amount + 1

    def set_id(self, id):
        self.id = id

    def find_instrument_id(self):
        global instrumentList
        for instr in instrumentList:
            if self == instr:
                self.name = instr.name
                self.id = instr.id
                return False
        if len(instrumentList) != 0:
            self.id = instrumentList[len(instrumentList) - 1].id + 1
        else:
            self.id = 1
        return True


class Error:
    def __init__(self, string, file):
        self.timestamp = time.time()
        self.msg = string
        self.file = file

    def get_str(self):
        return self.timestamp, self.msg, str(self.file)


class Musikstueck():
    def __init__(self, url):
        self.id = self.get_id()
        self.url = url
        self.artist = None
        self.title = ""
        self.misc = ""
        self.tempo = 0
        self.genre = ""
        self.epoche = ""
        self.uploaddate = None
        self.length = 0
        self.year = None
        self.key = ""
        self.instruments = []

    def get_id(self):
        global linkList
        if len(linkList) == 0:
            return 0
        return linkList[len(linkList) - 1].id + 1

    def __str__(self):
        return f"(url:{self.url}, artist:{self.artist}, title:{self.title}, misc:{self.misc})"

    def __repr__(self):
        return self.__str__()

    def get_str(self):
        return self.tempo, self.genre, self.uploaddate, self.length, self.year, self.key, self.epoche, self.title, self.url, self.artist.id, self.misc

    @property
    def find_metadata(self):
        global artistList
        global errors
        r = requests.get(self.url, allow_redirects=True)
        file_name = Path(self.url).name
        file_ext: str = Path(self.url).suffix
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
            if file_ext == 'xml' or file_ext == '.xml':
                try:
                    et = ET.parse(file_name)
                except:
                    errors.append(Error("Fehler bei ET.parse", self.url))
                    rem_file = pathlib.Path(file_name)
                    rem_file.unlink()
                    return False
                else:
                    pass
                root = et.getroot()
                root = root.tag
                if root != 'score-partwise':
                    rem_file = pathlib.Path(file_name)
                    rem_file.unlink()  # entfernt die unter file_name heruntergeladene Datei
                    return False
            # ERROR BREAK! ERROR LOG!
            score = converter.parse(file_name)
            var_tempo = score.metronomeMarkBoundaries(srcObj=None) #sucht BPM für Viertel heraus (also normale BPM)
            var_tempo = str(var_tempo)
            beat = re.sub("[^a-zA-Z]+", " ", var_tempo) #entfertn alle Sonderzeichen und Zahlen aus String mit Tempoangabe
            first, *middle, beat = beat.split() #ordnet beat letztes Wort zu, die Tempoangabe (z.B. half, full etc.)
            beat = beat.lower() #macht aus beat String einen lowercase, weil nur diese in music21 funktionieren
            var_tempo = re.search(r"<music21.tempo.MetronomeMark(.*?)>", var_tempo).group(1) #durchsucht String nach Tempo (Zahl)
            var_tempo = re.sub("[a-zA-Z, =]+", "", var_tempo) #wirft alle Buchstaben raus
            var_tempo = tempo.MetronomeMark(number=float(var_tempo), referent=beat) #es wird ein Tempoobjekt (var_tempo geschaffen, welches
            #die herausgesuchte BPM erhält und als referent den oben herausgefundenen beat
            var_tempo = var_tempo.getQuarterBPM() #rechnet BPM des Tempo Objekts auf Viertel um
            var_length = score.duration.quarterLength #gibt Dauer des ganzen Stücks in Viertel Noten an
            BPS = float(var_tempo) / 60 #BPS = Beats Per Second
            var_length = round(var_length / BPS)  #die Länge aus Viertelnoten geteilt durch die Viertelnoten pro Sekdunde
            #var_genre = ???
            #var_uploaddatum = ???
            #var_year = ???
            var_key = score.analyze('key')
            var_key = str(var_key)
            #var_epoche = ???
            #var_url = ???
            var_title = score.metadata.title
            var_artist = Kuenstler(0, score.metadata.composer)
            var_misc = score.metadata.all()
            var_misc = str(var_misc)
            var_misc = re.sub("[^0-9a-zA-Z]+", " ", var_misc)

            instruments = score.flat.getElementsByClass('Instrument')
            for instr in instruments:
                if instr.instrumentName is not None:
                    currInstrument = Instrument(0, instr.instrumentName)
                    if currInstrument.find_instrument_id():
                        instrumentList.append(currInstrument)
                    for x in self.instruments:
                        if x == currInstrument:
                            x.inc_amount()
                            break
                    else:
                        self.instruments.append(currInstrument)


            # var_instruments enthält nun alle Instrumente
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
            # print(var_title)

            # trägt Komponisten in DB ein, wenn sie nicht schon da sind

            if var_artist.find_artist_id():
                artistList.append(var_artist)

            self.tempo = var_tempo
            self.artist = var_artist
            self.title = var_title
            self.key = var_key
            self.misc = var_misc
            self.length = var_length
            rem_file = pathlib.Path(file_name)
            rem_file.unlink()  # entfernt die unter file_name heruntergeladene Datei
            return True

                # wie regeln wir es, dass Künstler nicht doppelt eingetragen werden?
                # BPM, Länge
        else:
            pass
        if file_ext == '.mid' or file_ext == 'midi':
            try:
                mid = MidiFile(file_name, clip=True)
            except:
                print("Midi nicht lesbar!")
                rem_file = pathlib.Path(file_name)
                rem_file.unlink()
                errors.append(Error("Midi nicht lesbar", self.url))
                return False
            else:
                pass
            try:
                score = converter.parse(file_name)
            except:
                print("Midi nicht lesbar!")
                errors.append(Error("Fehler bei converter.parse", self.url))
                rem_file = pathlib.Path(file_name)
                rem_file.unlink()
                return False
            else:
                pass
            # ERROR BREAK! ERROR LOG!
            try:
                var_length = mid.length
                var_length = round(var_length)
            except:
                rem_file = pathlib.Path(file_name)
                rem_file.unlink()
                errors.append(Error("Fehler bei mid.length", self.url))
                return False
            else:
                pass

            #sollte es bei mid.length einen Value Error hier geben, dann weil es asynchrone Midi-Files gibt,
            #die logischerweise auch keine Gesamtspielzeit haben
            var_misc = []
            var_data = ""
            var_title = ""
            var_artist = Kuenstler(0, "unbekannnt")
            var_tempo = 0
            var_key = score.analyze('key')
            var_key = str(var_key)
            var_url = ""
            midi_data = [] #leere Liste für Midi Daten
            meta_messages = []
            for i, track in enumerate(
                    mid.tracks):  # wenn es richtig benannte Instrumenten Tracks gibt, werden sie hier gesammelt
                # print('Track {}: {}'.format(i, track.name))
                for msg in track:
                    if msg.type == 'track_name':
                        #print(msg)
                        meta_messages.append((msg))
                        # var_artist = re.search(r"By (.*?)time=0", midi_data).group(1)
                        # var_title = re.search(r"track_name name=(.*?)time=0", midi_data).group(1)
            if len(meta_messages) >= 1:
                var_title = meta_messages[0].name


            #if "track_name" in midi_data:
                #var_title = re.search(r"track_name name=(.*?)time=0", midi_data).group(1)
            #if "key_signature" in midi_data:
                #var_key = re.search(r"key_signature key=(.*?)time=0", midi_data).group(1)
            tempo_midi_data = []
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'set_tempo' and "time=0":
                        var_tempo = msg.tempo
                        break
            #if len(tempo_midi_data) >= 1:
                #var_tempo = tempo_midi_data[0].tempo
            #if "set_tempo" in midi_data:
                #var_tempo = re.search(r"set_tempo tempo=(.*?) time=0", midi_data).group(1)
            if var_tempo != 0:
                var_tempo = int(var_tempo)
                var_tempo = round(60000000 / var_tempo, 0)
            #midi_data = []
            message_types = [
                "control_change",
                'note_on',
                'key_signature',
                'midi_port',
                'program_change',
                'set_tempo',
                'time_signature',
                'end_of_track',
                'pitchwheel',
                'sysex',
                'note_off'
            ]
            for track in mid.tracks:
                for msg in track:
                    if msg.type not in message_types:
                        if hasattr(msg, 'name'):
                            if msg.name != '':
                                midi_data.append(msg.name)
                        if hasattr(msg, 'text'):
                            if msg.text != '':
                                midi_data.append(msg.text)
            midi_data = str(midi_data)
            if "By " in midi_data:
                var_artist = re.search(r"By (.*?)'", midi_data).group(1)
                var_artist = Kuenstler(0, var_artist)
                if var_artist.find_artist_id():
                    artistList.append(var_artist)
            if "by " in midi_data:
                var_artist = re.search(r"by (.*?)'", midi_data).group(1)
                var_artist = Kuenstler(0, var_artist)
                if var_artist.find_artist_id():
                    artistList.append(var_artist)
            var_misc.append(midi_data)
            miscstr = ",".join(var_misc)
            miscstr = re.sub("[^0-9a-zA-Z]+", " ", miscstr)
            var_instruments = []
            instruments = score.recurse().getElementsByClass('Instrument')
            for instr in instruments:
                if instr.instrumentName is not None:
                    currInstrument = Instrument(0, instr.instrumentName)
                    if currInstrument.find_instrument_id():
                        instrumentList.append(currInstrument)
                    for x in self.instruments:
                        if x == currInstrument:
                            x.inc_amount()
                            break
                    else:
                        self.instruments.append(currInstrument)
            #var_instruments = re.sub("[^0-9a-zA-ZÀ-ÖØ-öø-ÿ+öÖäÄüÜ]+", " ", var_instruments)
            #var_instruments enthält Instrumente

            if var_title == '':
                var_title = file_name
            self.artist = var_artist
            self.title = var_title
            self.misc = miscstr
            self.tempo = var_tempo
            self.key = var_key
            self.length = var_length
            rem_file = pathlib.Path(file_name)
            rem_file.unlink()  # entfernt die unter file_name heruntergeladene Datei
            return True
        else:
            rem_file = pathlib.Path(file_name)
            rem_file.unlink()  # entfernt die unter file_name heruntergeladene Datei
            pass
        return False

class Url():
    def __init__(self, url, parent, last):
        self.url = url
        self.parent = parent
        self.last = last

    def __eq__(self, other):
        if type(other) == str:
            return self.url == other
        return ((self.url, self.last)) == ((other.url, other.last))

    def __contains__(self, item):
        return self.url == item.url

    def get_str(self):
        return self.url, self.last, self.parent

    def set_url(self, url):
        self.url = url

    def set_last(self, last):
        self.last = last

    def __str__(self):
        return self.url


def crawler(url):
    try: #Versucht, Verbindung zur Seite zu gelangen
        source_code = requests.get(url)
    except:
        errors.append(Error("Fehler beim Crawlen", url))
        return True
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, features="html.parser")
    reg = re.compile(r"\.midi?|\.xml$")
    items = soup.find_all("a")
    for i in range(len(items)):
        link = items[i]
        href = link.get('href')
        nexturl = urllib.parse.urljoin(str(url), str(href))
        if i == len(items) - 1:
            last = 1
        else:
            last = 0
        nexturl = Url(nexturl, url, last)
        with queueLock:
            if nexturl.url == url or str(href) == "None":
                continue
            cnt = False
            for x in hrefList:
                if x.url == nexturl.url:
                    cnt = True

            for j in range(i):
                if str(link.get("href")) == str(items[j].get("href")):
                    cnt = True
                    break
            if not cnt:
                if reg.search(nexturl.url):
                    # HIER KOMMT DER METADATA CODE
                    new_music = Musikstueck(nexturl.url)
                    print(f"FOUND FILE {nexturl.url}")
                    if new_music.find_metadata:
                        linkList.append(new_music)
                        hrefList.append(nexturl)
                else:
                    hrefList.append(nexturl)
                    q.put(nexturl.url)
        # with queueLock:
        #     hrefList.append(url)
    return True


def startup():
    cursor = mydb.cursor(buffered=True)
    cursor.execute("SELECT url FROM crawled_urls WHERE url NOT IN (SELECT ParentId FROM crawled_urls WHERE last = 1)")
    global last_amount_crawled
    global last_amount_artist
    global last_amount_links
    global last_amount_instruments
    global q, hrefList, artistList, instrumentList
    print(f"FOUND {cursor.rowcount} Websites still to crawl")
    if cursor.rowcount > 0:
        for entry in cursor:
            # print(f"put {entry[0]} to q")
            q.put(entry[0])
    else:
        print(f"put {starturl} to q")
        q.put(starturl)

    cursor = mydb.cursor(buffered=True)
    cursor.execute("SELECT DISTINCT ParentId FROM crawled_urls WHERE last = 1")
    cursor_music = mydb.cursor(buffered=True)
    cursor_music.execute("SELECT url FROM musikstueck")
    print(cursor)
    music_rows = + cursor_music.rowcount
    if music_rows == -1:
        music_rows = 0
    if cursor.rowcount > 0:
        hrefList = [None] * (cursor.rowcount + music_rows)
    print(len(hrefList))
    for i, entry in enumerate(cursor):
        print(f"{i} is now {entry[0]}")
        hrefList[i] = Url(entry[0], '', 0)

    for i, entry in enumerate(cursor_music):
        print(f"{i + cursor.rowcount} is now {entry[0]}")
        hrefList[i + cursor.rowcount] = Url(entry[0], '', 0)
    last_amount_artist = len(artistList)

    last_amount_crawled = len(hrefList)

    cursor = mydb.cursor(buffered=True)
    cursor.execute("SELECT id, name FROM kuenstler")
    if cursor.rowcount > 0:
        artistList = [None] * cursor.rowcount
        for i, entry in enumerate(cursor):
            artistList[i] = Kuenstler(entry[0], entry[1])
    last_amount_artist = len(artistList)

    cursor = mydb.cursor(buffered=True)
    cursor.execute("SELECT id, name FROM instrument")
    if cursor.rowcount > 0:
        instrumentList = [None] * cursor.rowcount
        for i, entry in enumerate(cursor):
            instrumentList[i] = Instrument(entry[0], entry[1])
    last_amount_instruments = len(instrumentList)




# Variablen, die bestimmen, wann in die Datenbank gepusht wird
last_amount_crawled = 0
last_amount_links = 0
last_amount_artist = 0
last_amount_instruments = 0
database_push_amount = 100

queueLock = threading.Lock()
linkList = []
hrefList = []
artistList = []
instrumentList = []
errors = []
starturl = 'https://sing-kikk.de/'
q = queue.Queue()
startup()

threadCount = 4
threads = []
start = time.time()

for i in range(threadCount):
    t = CrawlThread("", i)
    threads.append(t)
    t.start()

for x in threads:
    x.join()
end = time.time()