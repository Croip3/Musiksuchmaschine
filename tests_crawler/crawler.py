import requests
from bs4 import BeautifulSoup
import re
import threading
import queue
import time
import mysql.connector


mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="3X2SDuKU8v5",
        database="musiksuchmaschine"
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
                print(f"THREAD {self.title} going for {self.url}")
                crawler(self.url)
                global last_amount_crawled
                global database_push_amount
                d = len(hrefList) - last_amount_crawled
                if d > database_push_amount:
                    global mydb
                    if not mydb.is_connected():
                        mydb = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="3X2SDuKU8v5",
                            database="musiksuchmaschine"
                        )
                    for k in range(last_amount_crawled, len(hrefList)):
                        mycursor = mydb.cursor()
                        sql = "INSERT INTO crawled_urls (id, url, timestamp) VALUES (NULL, %s, NULL)"
                        val = (hrefList[k], )
                        mycursor.execute(sql, val)
                        print(mycursor.rowcount, "record inserted.")
                    mydb.commit()
                    last_amount_crawled = len(hrefList)
                q.task_done()


def crawler(url):
    # print(f"URL: {url}")
    # if url in hrefList:
    #     return True
    if len(hrefList) > 500: #Begrenzung, damit es nicht so lange dauert
        return False
    try: #Versucht, Verbindung zur Seite zu gelangen
        source_code = requests.get(url)
    except:
        # print(f"ERROR AT CRAWLING {url}")
        return True
    print(f"SEARCHING {url}")
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, features="html.parser")
    reg = re.compile(r"\.midi?$")
    print("test")
    items = soup.find_all("a")
    for i in range(len(items)):
        link = items[i]
        href = link.get('href')
        if not re.search(r"^http", str(href)):
            nexturl = starturl + str(href)
        else:
            nexturl = str(href)
        with queueLock:
            if nexturl == url or str(href) == "None":
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
            if reg.search(str(href)):
                linkList.append(link)
                print("\tADDED LINK:")
                print("\t" + nexturl)
                hrefList.append(nexturl)
            else:
                hrefList.append(nexturl)
                q.put(nexturl)
        # with queueLock:
        #     hrefList.append(url)
    return True


last_amount_crawled = 0
database_push_amount = 100
queueLock = threading.Lock()
linkList = []
hrefList = []
starturl = 'https://bitmidi.com'
q = queue.Queue()
q.put(starturl)
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
    print(str(x.get('href')))


# crawler(starturl, 0)



