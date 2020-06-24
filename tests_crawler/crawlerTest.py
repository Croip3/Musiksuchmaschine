import requests
from bs4 import BeautifulSoup
import re


def test_spider(max_pages):
    page = 1
    while page <= max_pages:
        url =  'https://bitmidi.com/'
        source_code = requests.get(url)
        print(requests.get(url))
        plain_text = source_code.text
        #print(plain_text)
        soup = BeautifulSoup(plain_text, features="html.parser")

        links = soup.findAll(string=re.compile("h2"))
        print(links)

        for link in soup.findAll(href = re.compile("\.mid$")):
            print("link")
            print(link)
            #href = link.get('href')
            #print(href)
            #title = link.href
            #print(title)
    page += 1

test_spider(2)
print("fertig")