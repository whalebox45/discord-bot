
import argparse
from asyncore import read
import csv
import re
from time import sleep
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import sys

sys.setrecursionlimit(5000)

# page = 1
ua = UserAgent()

parser = argparse.ArgumentParser()
parser.add_argument("pack")
args = parser.parse_args()

if not args.pack:
    exit(1)


for page in range(1,10):
    print(page)
    page_request = requests.get(
    'http://220.134.173.17/gameking/card/ocg_list.asp?call_item=1&call_data=' + args.pack + '&call_sql=Select%20*%20from%20ocg%20where%20ocg_no%20like%20%27SR13-JP%A2H%27%20order%20by%20ocg_no%20asc&Page='+str(page)
        , headers={"User-Agent": ua.random})

    soup = BeautifulSoup(page_request.content, 'html.parser')

    soup.encode = "utf-8"

    card_number = soup.find(text="卡號")
    
    cur = card_number.parent.parent.parent

    rows = cur.findChildren("tr")
    searched_cards = []
    for r in rows:
        cell_texts = [str(cell.text).replace(
            '\n', '').replace('\u3000', '') for cell in r]
        if "卡號" not in cell_texts:
            searched_cards.append(cell_texts)
            with open('output.csv','a',encoding='utf-8') as csv_file:
                wr = csv.writer(csv_file)
                wr.writerow(cell_texts)
            print(cell_texts)
    
    sleep(0.5)
