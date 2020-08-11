import requests
from bs4 import BeautifulSoup
import re
import threading
import queue
import time
import mysql.connector




class CrawlThread(threading.Thread):
    def __init__(self, url, title):
        threading.Thread.__init__(self)
        self.url = url
        self.title = title

    def run(self):
        while True:
            if not q.empty():
                # queueLock.acquire()
                self.url = q.get()
                # queueLock.release()
                # print(f"THREAD {self.title} going for {self.url}")
                # rval = crawler(self.url)
                # print(rval)
                if not crawler(self.url):
                    break
                q.task_done()


def crawler(url):
    # print(f"URL: {url}")
    # if url in hrefList:
    #     return True
    if "@" in url:
        return True
    if len(linkList) > 1000: #Begrenzung, damit es nicht so lange dauert
        return False
    try: #Versucht, Verbindung zur Seite zu gelangen
        source_code = requests.get(url)
    except:
        print(f"ERROR AT CRAWLING {url}")
        return True
    # print(f"SEARCHING {url}")
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, features="html.parser")
    reg = re.compile(r"\.midi?$")
    items = soup.find_all("a")
    for i in range(len(items)):
        link = items[i]
        href = str(link.get('href'))
        # print(f"\t{href}")
        if len(href) == 0 or "@" in href:
            continue
        if not re.search(r"^http", href):
            if href[0] != '/':
                href = '/' + href
            nexturl = url + href
        else:
            nexturl = href
        with queueLock:
            if nexturl == url or href == "None":
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
                # print("\tADDED LINK:")
                # print("\t" + nexturl)
                hrefList.append(nexturl)
            else:
                hrefList.append(nexturl)
                q.put(nexturl)
        # with queueLock:
        #     hrefList.append(url)
    return True


queueLock = threading.Lock()

for k in range(32):
    linkList = []
    hrefList = []
    q = queue.Queue()
    # starturl = ['https://bitmidi.com']
    starturl = ['https://bitmidi.com', 'http://www.telewerkstatt.at', 'https://www.mfiles.co.uk/midi-files.htm']
    for s in starturl:
        q.put(s)
    threadCount = k + 1
    threads = []
    start = time.time()
    for i in range(threadCount):
        t = CrawlThread("", i)
        threads.append(t)
        t.start()
    for x in threads:
        x.join()
    end = time.time()
    print(f"\n USED {k + 1} THREADS: NEEDED {end - start} seconds")
    print(f"SEARCHED {len(hrefList)} PAGES")
    print(f"{len(hrefList)/(end-start)} PAGES PER SECOND")
    print(f"FOUND {len(linkList)} MIDI FILES")
    print(f"SIZE OF REMAINING QUEUE {q.qsize()}\n")

# crawler(starturl, 0)



