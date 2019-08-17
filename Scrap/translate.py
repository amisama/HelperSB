import requests, json, sys
from bs4 import BeautifulSoup as bsoup

class TranslateKyu:
    def __init__(self):
        self.host = "https://translate.google.com/m?hl=en"
    def translate(self, to, query):
        query = query.replace(" ","+")
        url = "{}&sl=auto&tl={}&ie=UTF-8&prev=_m&q={}".format(self.host,to,query)
        r = requests.get(url)
        data = bsoup(r.content,'lxml')
        result = data.findAll('div',{'class':'t0'})[0]
        return result.text
