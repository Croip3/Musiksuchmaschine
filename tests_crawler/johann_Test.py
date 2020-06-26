import requests
from bs4 import BeautifulSoup
import re
import threading
import queue
import time


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
                # rval = crawler(self.url)
                # print(rval)
                if not crawler(self.url):
                    break


def crawler(url):
    # print(f"URL: {url}")
    print(len(hrefList))
    if url in hrefList:
        return True
    if len(hrefList) > 5000: #Begrenzung, damit es nicht so lange dauert
        return False
    try: #Versucht, Verbindung zur Seite zu gelangen
        source_code = requests.get(url)
    except:
        print(f"ERROR AT CRAWLING {url}")
        return True
    print(f"SEARCHING {url}")
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, features="html.parser")
    reg = re.compile(r"\.midi?$")
    items = soup.find_all("a")
    # for itemo in items:
    #     print(f"\t{itemo.get('href')}")
      # Fügt die aktuelle URL zu gecrawlt hinzu
    for link in items:
        href = link.get('href')
        if not re.search(r"^http", str(href)):
            nexturl = starturl + str(href)
        else:
            nexturl = str(href)
        with queueLock:
            print(hrefList)
            if nexturl == url or str(href) == "None":
                print(f"{nexturl} is Same Site")
                continue
            if nexturl in hrefList:
                print(f"\n{nexturl} has already been crawled")
                continue
            print("This comes after")
            if reg.search(str(href)):
                linkList.append(link)
                print("\tADDED LINK:")
                print("\t" + nexturl)
                hrefList.append(nexturl)
            else:
                print(f"{nexturl} has been put to Q!")
                q.put(nexturl)
    with queueLock:
        hrefList.append(url)
    return True


queueLock = threading.Lock()
linkList = []
hrefList = []
starturl = 'https://bitmidi.com'
q = queue.Queue()
q.put(starturl)
threadCount = 1
threads = []
for i in range(threadCount):
    t = CrawlThread("", i)
    threads.append(t)
    t.start()

for x in threads:
    x.join()

# crawler(starturl, 0)


print(f"\n SEARCHED {len(hrefList)} PAGES")
for item in hrefList:
    print(item)
print(f"\n FOUND {len(linkList)} MIDI FILES!")
for item in linkList:
    print(item.string)
    print(item.get('href'))

