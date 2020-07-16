from urllib.request import urlretrieve
from urllib.request import urlopen
from urllib.error import HTTPError, ContentTooShortError
from bs4 import BeautifulSoup
import re
import os
import logging
from download import download_file_multi_thread
from download import normal_download

BASE_URL = "https://bulkdata.uspto.gov/"
PATENT_URL = "data/patent/grant/redbook/fulltext/"
APPLICATION_URL = "data/patent/application/redbook/fulltext/"

DOWNLOAD_DIRECTORY = "downloaded"


def get_link(text):

    # return None # test code

    try:
        values = text.split(',')
        for value in values:
            if value.find("eventLbl"):
                return value.split(':')[2].strip()

    except Exception as e:
        print(e)

    return None


def file_is_downloaded(file_name, upload_day):
    return os.path.exists(file_name)


def handle_patent_detail_page(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
        return None
        
    try:
        bs_obj = BeautifulSoup(html.read(), "lxml")
        div = bs_obj.find("div", {"id":"usptoGlobalHeader"})
        size = 0

        for tr in div.findAll("table")[1].findAll("tr"):
            tds = tr.findAll("td")
            size = size + int(tds[1].getText())
            file_url = tds[0].a.attrs["href"]
            upload_day = tds[2].getText()
            if file_is_downloaded(DOWNLOAD_DIRECTORY + "/" + file_url, upload_day):
                logging.info("file: %s upload: %s was downloaded previously, won't handle" % (file_url, upload_day))
                continue

            download_url = url + "/" + file_url

            logging.debug(download_url)

            try:

                return_value = download_file_multi_thread(download_url, DOWNLOAD_DIRECTORY)

                if return_value != 0:
                    logging.info("file: %s upload: %s multi-thread download failure" % (file_url, upload_day))
                    if normal_download(download_url, DOWNLOAD_DIRECTORY) == 0:
                        logging.info("file: %s upload: %s is downloaded normally" % (file_url, upload_day))
                    else:
                        logging.info("file: %s upload: %s normal download failure" % (file_url, upload_day))
                else:
                    logging.info("file: %s upload: %s is downloaded by multi thread" % (file_url, upload_day))

            except ContentTooShortError as e:
                logging.error(e)

        return size
     
    except AttributeError as e:
        logging.error(e)
        return None
    return title


# handle application data
def handle_application_detail_page(url):
    return None


def handle_home_page(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        logging.error(e)
        return 1
    try:
        bs_obj = BeautifulSoup(html.read(), "lxml")
        title = bs_obj.head.title.getText()
        logging.info(title)

        # handle patent linkers
        for link in bs_obj.find("div", {"id": "mainArea"}).findAll("a", href=re.compile(PATENT_URL)):
            if 'href' in link.attrs:
                logging.debug(link.attrs['href'])
                handle_patent_detail_page(link.attrs['href'])

        # handle application linkers
        for link in bs_obj.find("div", {"id": "mainArea"}).findAll("a", href=re.compile(APPLICATION_URL)):
            if 'href' in link.attrs:
                logging.debug(link.attrs['href'])
                # todo we may need different method to decide which table to input
                handle_patent_detail_page(link.attrs['href'])
        
    except AttributeError as e:
        logging.error(e)
        return 2

    return 0


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    if not os.path.exists(DOWNLOAD_DIRECTORY):
        os.makedirs(DOWNLOAD_DIRECTORY)

    ret = handle_home_page(BASE_URL)

    if ret != 0:
        logging.error("Home page of bulk data download can't be access!")
    else:
        logging.info("ome page of bulk data download handled")
