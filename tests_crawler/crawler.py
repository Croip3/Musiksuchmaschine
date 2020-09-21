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
from xml.etree import ElementTree as ET




dbconfig = { "host": "localhost",
        "user": "root",
        # password:"3X2SDuKU8v5",
        "password": "",
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
                global  last_amount_artist
                print(f"THREAD {self.title} going for {self.url}")
                with queueLock:
                    d = len(hrefList) - last_amount_crawled
                    print(f'THREAD {self.title} has a d of {d}')
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
                        records = []
                        for k in range(last_amount_crawled, len(hrefList)):
                            records.append(hrefList[k].get_str())
                        mycursor = mydb.cursor()
                        sql = "INSERT INTO crawled_urls VALUES (%s, %s, %s, %s, %s)"
                        mycursor.executemany(sql, records)
                        print(mycursor.rowcount, "record inserted.")

                        records = []
                        for k in range(last_amount_links, len(linkList)):
                            records.append(linkList[k].get_str())
                        mycursor2 = mydb.cursor()
                        sql2 = "INSERT INTO musikstueck VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        mycursor2.executemany(sql2, records)

                        records = []
                        for k in range(last_amount_artist, len(artistList)):
                            records.append(artistList[k].get_str())
                        mycursor2 = mydb.cursor()
                        sql2 = "INSERT INTO kuenstler VALUES (%s, %s)"
                        mycursor2.executemany(sql2, records)

                        mydb.commit()

                        last_amount_crawled = len(hrefList)
                        last_amount_links = len(linkList)
                        last_amount_artist = len(artistList)
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





class Musikstueck():
    def __init__(self, url):
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

    def __str__(self):
        return f"(url:{self.url}, artist:{self.artist}, title:{self.title}, misc:{self.misc})"

    def __repr__(self):
        return self.__str__()

    def get_str(self):
        return "NULL", self.tempo, self.genre, self.uploaddate, self.length, self.year, self.key, self.epoche, self.title, self.url, self.artist.id, self.misc

    @property
    def find_metadata(self):
        global artistList
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
                et = ET.parse(file_name)
                root = et.getroot()
                root = root.tag
                if root != 'score-partwise':
                    print("Kein Music XML!")
                    rem_file = pathlib.Path(file_name)
                    rem_file.unlink()  # entfernt die unter file_name heruntergeladene Datei
                    return False
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
            var_length = str(datetime.timedelta(seconds=var_length)) #wandelt Sekunden des Strings in Zeitangabe
            var_length = str(var_length)
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
            var_instruments = []
            instruments = score
            for instrument in instruments:
                instrument = str(instrument)
                instrument = re.search(r"<music21.stream.Part (.*?)>", instrument)
                if instrument is not None:
                    var_instruments.append(instrument.group(1))
            var_instruments = str(var_instruments)
            var_instruments = re.sub("[^0-9a-zA-ZÀ-ÖØ-öø-ÿ+öÖäÄüÜ]+", " ", var_instruments)
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
            mid = MidiFile(file_name, clip=True)
            var_length = mid.length
            var_length = round(var_length)
            var_length = str(datetime.timedelta(seconds=var_length))
            #sollte es bei mid.length einen Value Error hier geben, dann weil es asynchrone Midi-Files gibt,
            #die logischerweise auch keine Gesamtspielzeit haben
            var_misc = []
            var_data = ""
            var_title = ""
            var_artist = Kuenstler(0, "unbekannnt")
            var_tempo = ""
            var_key = ""
            var_url = ""
            midi_data = [] #leere Liste für Midi Daten
            for track in mid.tracks:
                midi_data.append(track)
                for msg in mid.tracks[0]:
                    midi_data.append(msg)

            midi_data = str(midi_data)
            if "track_name" in midi_data:
                var_title = re.search(r"track_name name=(.*?)time=0", midi_data).group(1)
            if "key_signature" in midi_data:
                var_key = re.search(r"key_signature key=(.*?)time=0", midi_data).group(1)
            if "set_tempo" in midi_data:
                var_tempo = re.search(r"set_tempo tempo=(.*?) time=0", midi_data).group(1)
                var_tempo = int(var_tempo)
                var_tempo = round(60000000 / var_tempo, 0)
            if "By " in midi_data:
                var_artist = re.search(r"By (.*?)time=0", midi_data).group(1)
                var_artist = Kuenstler(0, var_artist)
                if var_artist.find_artist_id():
                    artistList.append(var_artist)
            if "by " in midi_data:
                var_artist = re.search(r"by (.*?)time=0", midi_data).group(1)
                var_artist = Kuenstler(0, var_artist)
                if var_artist.find_artist_id():
                    artistList.append(var_artist)
            var_misc.append(midi_data)
            miscstr = ",".join(var_misc)
            miscstr = re.sub("[^0-9a-zA-Z]+", " ", miscstr)
            var_instruments = []
            for instrument in midi_data:
                instrument = str(instrument)
                instrument = re.search(r"<midi track '(.*?)'", instrument)
                if instrument is not None:
                    var_instruments.append(instrument.group(1))
            var_instruments = str(var_instruments)
            var_instruments = re.sub("[^0-9a-zA-ZÀ-ÖØ-öø-ÿ+öÖäÄüÜ]+", " ", var_instruments)
            #var_instruments enthält Instrumente


            self.artist = var_artist
            self.title = var_title
            self.misc = miscstr
            self.tempo = var_tempo
            self.key = var_key
            self.length = var_length
            rem_file = pathlib.Path(file_name)
            rem_file.unlink()  # entfernt die unter file_name heruntergeladene Datei
            return True
            # print(mycursor.rowcount, "record inserted.")
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
        return "NULL", self.url, self.last, self.parent, "NULL"

    def set_url(self, url):
        self.url = url

    def set_last(self, last):
        self.last = last

    def __str__(self):
        return self.url


def crawler(url):
    # print(f"URL: {url}")
    # if url in hrefList:
    #     return True
    if len(hrefList) > 1000: #Begrenzung, damit es nicht so lange dauert
        return False
    try: #Versucht, Verbindung zur Seite zu gelangen
        source_code = requests.get(url)
    except:
        # print(f"ERROR AT CRAWLING {url}")
        return True
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, features="html.parser")
    reg = re.compile(r"\.midi?|\.xml$")
    items = soup.find_all("a")
    for i in range(len(items)):
        link = items[i]
        href = link.get('href')
        nexturl = urllib.parse.urljoin(url, str(href))
        if i == len(items) - 1:
            last = 1
        else:
            last = 0
        nexturl = Url(nexturl, url, last)
        with queueLock:
            if nexturl.url == url or str(href) == "None":
                continue
            if nexturl in hrefList:
                continue
            cnt = False
            for j in range(i):
                if str(link.get("href")) == str(items[j].get("href")):
                    cnt = True
                    break
            if cnt:
                continue
            if reg.search(nexturl.url):
                # HIER KOMMT DER METADATA CODE
                new_music = Musikstueck(nexturl.url)
                print(f"FOUND FILE {nexturl.url}")
                if new_music.find_metadata:
                    linkList.append(new_music)
                    hrefList.append(nexturl)
                    print(linkList)
            else:
                hrefList.append(nexturl)
                q.put(nexturl.url)
        # with queueLock:
        #     hrefList.append(url)
    return True


def startup():
    cursor = mydb.cursor()
    cursor.execute("SELECT url FROM crawled_urls WHERE url NOT IN (SELECT ParentId FROM crawled_urls WHERE last = 1)")
    result = cursor.fetchall()
    global last_amount_crawled
    global last_amount_artist
    global q
    if cursor.rowcount > 0:
        for entry in result:
            print(f"put {entry[0]} to q")
            q.put(entry[0])
    else:
        print(f"put {starturl} to q")
        q.put(starturl)
    cursor = mydb.cursor()
    cursor.execute("SELECT DISTINCT ParentId FROM crawled_urls WHERE last = 1")
    result = cursor.fetchall()
    for entry in result:
        hrefList.append(Url(entry[0], '', 0))
    last_amount_crawled = len(hrefList)

    cursor = mydb.cursor()
    cursor.execute("SELECT id, name FROM kuenstler")
    result = cursor.fetchall()
    for entry in result:
        artistList.append(Kuenstler(entry[0], entry[1]))
    last_amount_artist = len(artistList)




# Variablen, die bestimmen, wann in die Datenbank gepusht wird
last_amount_crawled = 0
last_amount_links = 0
last_amount_artist = 0
database_push_amount = 100

queueLock = threading.Lock()
linkList = []
hrefList = []
artistList = []
starturl = 'http://sing-kikk.de/'
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

print(f"\nFOUND {len(linkList)} MIDI FILES IN {end-start} seconds\nFOLLOWING MIDI FILES WERE FOUND")
for x in linkList:
    print(x)