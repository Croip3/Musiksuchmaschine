import requests
from bs4 import BeautifulSoup
import re
import threading
import queue


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
                print(f"THREAD {self.title} going for {self.url}")
                if not crawler(self.url):
                    break


def crawler(url):
    # print(f"URL: {url}")
    if len(hrefList) > 50: #Begrenzung, damit es nicht so lange dauert
        return False
    try: #Versucht, Verbindung zur Seite zu gelangen
        source_code = requests.get(url)
    except:
        print(f"ERROR AT CRAWLING {url}")
        return
    print(f"SEARCHING {url}")
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, features="html.parser")
    reg = re.compile(r"\.midi?$")
    items = soup.find_all("a")
    hrefList.append(url)  # Fügt die aktuelle URL zu gecrawlt hinzu
    for link in items:
        href = link.get('href')
        nexturl = starturl + str(href)
        # queueLock.acquire()
        if nexturl in hrefList or nexturl == url or str(href) == "None":
            continue
        if reg.search(str(href)):
            linkList.append(link)
            print("\tADDED LINK:")
            print("\t" + nexturl)
            hrefList.append(nexturl)
        else:
            q.put(nexturl)
        # queueLock.release()


queueLock = threading.Lock()
linkList = []
hrefList = []
starturl = 'https://bitmidi.com'
q = queue.Queue()
q.put(starturl)
threadCount = 8
threads = []
for i in range(threadCount):
    t = CrawlThread("", i)
    threads.append(t)
    t.start()

for x in threads:
    x.join()

# crawler(starturl, 0)

print("fertig")
print(linkList)
for item in hrefList:
    print(item)
for item in linkList:
    print(item.string)
    print(item.get('href'))

