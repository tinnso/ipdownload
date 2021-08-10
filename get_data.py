from urllib.request import urlopen

from fake_useragent import UserAgent
from bs4 import *
import requests

url = "http://patft.uspto.gov/netacgi/nph-Parser?patentnumber=5123456"
ua = UserAgent()
agent = ua.random
headers= {"User-Agent":agent}

res = requests.get(url, headers=headers)
#cookies = res.cookies

print (res.text)

bs_obj = BeautifulSoup(res.text, "lxml")
meta = bs_obj.select('html > head > meta')

result_url = meta[0].attrs['content'].split(';')[1]
result_url = result_url.replace("URL=", "http://patft.uspto.gov")
print(result_url)

#res = requests.get(result_url, headers=headers, cookies=cookies)
res = requests.get(result_url, headers=headers)
print (res.text)


#http://patft.uspto.gov/netacgi/nph-Parser?Sect2=PTO1&Sect2=HITOFF&p=1&u=%2Fnetahtml%2FPTO%2Fsearch-bool.html&r=1&f=G&l=50&d=PALL&RefSrch=yes&Query=PN%2F2214110
result_url= "http://patft.uspto.gov/netacgi/nph-Parser?Sect2=PTO1&Sect2=HITOFF&p=1&u=%2Fnetahtml%2FPTO%2Fsearch-bool.html&r=1&f=G&l=50&d=PALL&RefSrch=yes&Query=PN%2F2214110"
res = requests.get(result_url, headers=headers)
print (res.text)