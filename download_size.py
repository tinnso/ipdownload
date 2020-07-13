from urllib.request import urlretrieve
from urllib.request import urlopen
from urllib.error import HTTPError, ContentTooShortError
from bs4 import BeautifulSoup
import re
import os

BASE_URL = "https://bulkdata.uspto.gov/"
PATENT_URL = "data/patent/grant/redbook/fulltext/"
APPLICATION_URL = "data/patent/application/redbook/fulltext/"

DOWNLOAD_DIRECTORY = "downloaded"


# call back function of download
def download_callback(block_number, block_size, data_size):
    per = 100.0 * block_number * block_size / data_size
    if per > 100:
        per = 100
    print('total size %d, %.2f%%' % (data_size, per))


def handle_patent_detail_page(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print("url open error")
        print(url)
        return None
        
    try:
        bs_obj = BeautifulSoup(html.read(), "lxml")
        div = bs_obj.find("div", {"id":"usptoGlobalHeader"})
        size = 0

        for tr in div.findAll("table")[1].findAll("tr"):
            tds = tr.findAll("td")
            size = size + int(tds[1].getText())
            file_url = tds[0].a.attrs["href"]
            print(file_url)
            download_url = url + "/" + file_url
            local_url = DOWNLOAD_DIRECTORY + "/" + file_url
            print(download_url)

            if not os.path.exists(DOWNLOAD_DIRECTORY):
                os.makedirs(DOWNLOAD_DIRECTORY)

            try:
                urlretrieve(download_url, local_url, download_callback)
            except ContentTooShortError as e:
                print(e)

        return size
     
    except AttributeError as e:
        print(e)
        return None
    return title


# handle application data
def handle_application_detail_page(url):
    return None


def handle_home_page(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    try:
        bs_obj = BeautifulSoup(html.read(), "lxml")
        title = bs_obj.head.title.getText()
        print(title)

        # handle patent linkers
        for link in bs_obj.find("div", {"id": "mainArea"}).findAll("a", href=re.compile(PATENT_URL)):
            if 'href' in link.attrs:
                print(link.attrs['href'])
                print(handle_patent_detail_page(link.attrs['href']))

        # handle application linkers
        for link in bs_obj.find("div", {"id": "mainArea"}).findAll("a", href=re.compile(APPLICATION_URL)):
            if 'href' in link.attrs:
                print(link.attrs['href'])
                print(handle_patent_detail_page(link.attrs['href']))
        
    except AttributeError as e:
        print(e)
        return None
    return title


ret = handle_home_page(BASE_URL)

if ret is None:
    print("Home page of bulk data download can't be access!")
else:
    print(ret)
