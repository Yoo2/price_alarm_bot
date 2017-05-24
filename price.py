import sys
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
import re

TARGET_URL = "http://finance.naver.com/item/sise.nhn?code="

def getPrice(code = ''):
    url = urllib.request.urlopen(TARGET_URL + quote(code))
    soup = BeautifulSoup(url, 'lxml', from_encoding='utf-8')
    text = ''
    for item in soup.find_all('strong', id='_nowVal'):
        text += str(item.find_all(text=True))

    price = ''
    for t in text:
        if t.isdigit():
            price += t

    if price == '':
        return None

    return int(price)

def getName(code = ''):
    url = urllib.request.urlopen(TARGET_URL + quote(code))
    soup = BeautifulSoup(url, 'lxml', from_encoding='utf-8')

    arr = []
    for item in soup.find_all('div', {"class", "wrap_company"}):
        arr = item.find_all(text=True)

    if len(arr) == 0:
        return None

    return arr[1]
