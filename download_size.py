from urllib.request import urlretrieve
from urllib.request import urlopen
from urllib.error import HTTPError, ContentTooShortError
from bs4 import BeautifulSoup
import re
import os

#baseUrl = "https://bulkdata.uspto.gov/"
downloadDirectory = "downloaded"

def downloadCallback(blocknumber, blocksize, datasize):
    per = 100.0*blocknumber*blocksize/datasize
    if per > 100:
        per = 100
    print('%.2f%%' % per)

def handlePatentDetailPage(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print("url open error")
        print(url)
        return None
        
    try:
        bsObj = BeautifulSoup(html.read(), "lxml")
        div = bsObj.find("div", {"id":"usptoGlobalHeader"})
        size = 0
        

        for tr in div.findAll("table")[1].findAll("tr"):
        	#print(tr)
        	#print(tr.findAll("td")[1].getText())
            tds = tr.findAll("td")
            size = size + int(tds[1].getText())
            fileUrl = tds[0].a.attrs["href"]
            print(fileUrl)
            downloadUrl = url + "/"+ fileUrl
            print(downloadUrl)
            if not os.path.exists(downloadDirectory):
                os.makedirs(downloadDirectory)
            try:
                urlretrieve(downloadUrl, downloadDirectory + "/" + fileUrl, downloadCallback)
            except ContentTooShortError as e:
                print(e)

        return size
     
    except AttributeError as e:
        print (e)
        return None
    return title

def getTitle(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print (e)
    try:
        bsObj = BeautifulSoup(html.read(), "lxml")
        title = bsObj.head.title.getText()
        print(title)
        
        for link in bsObj.find("div", {"id":"mainArea"}).findAll("a", href=re.compile("/redbook\/fulltext/")):
            if 'href' in link.attrs:
                
                print(link.attrs['href'])
                print(handlePatentDetailPage(link.attrs['href']))
                
        
    except AttributeError as e:
        print (e)
        return None
    return title
    
title = getTitle("https://bulkdata.uspto.gov/")
if title == None:
    print("Title could not befound")
else:
    print(title)
