import os
from dotenv import load_dotenv

import interactions
import requests
from bs4 import BeautifulSoup

import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = interactions.Client(token=TOKEN, default_scope=False)


@bot.command(
    name="win_deck",
    description="顯示每周台大卡牌研究社遊戲王上位餅圖與比例"
)
async def win_deck(ctx: interactions.CommandContext):
    await ctx.send("請問你要選哪一個時段的上位餅圖？")

    webdata = requests.get(
    "https://ntucgm.blogspot.com/search/label/OCG%E8%B3%BD%E4%BA%8B-Meta%E5%B1%95%E6%9C%9B/")

    soup = BeautifulSoup(webdata.text, "html.parser")

    sel = soup.findAll("h3", {'class': "entry-title"})

    a = []
    for s in sel:
        a.append({
            "link": s.findChild("a")["href"],
            "title": str(s.find("div", {'class': 'r-snippetized'}).text).strip('\n')
            })
    option_str = ""
    for x in a[:9]:
        option_str+= str(a.index(x)+1) + ': ' + x['title'] + '\n'

    week_menu = interactions.SelectMenu(
        options=[
            interactions.SelectOption(
                label=str(a.index(x)+1) +': '+ x['title'],
                value=x['link'],
            )
             for x in a[:9]    
            ],
        custom_id="week_select",
    )    
        
    await ctx.send('```\n'+option_str+'\n```',components=week_menu)
    

@bot.component("week_select")
async def week(ctx, value):

    webdata = requests.get(value[0])

    soup = BeautifulSoup(webdata.text, "html.parser")

    sel = soup.find("div",{'class':'post'})

    await ctx.send(sel.find_next('img')["src"])

    sel = soup.find_all('b')

    regex = re.compile("^.*[0-9](\s|)[0-9]+\.[0-9]\%.*")

    b = ""

    for s in sel:
        rs = regex.search(s.text)
        if rs is not None:
            b+=str(rs.group(0)) + '\n'

    await ctx.send('```\n'+str(b)+'\n```')

@bot.command(
    name="card_find",
    description="依據卡號、密碼或名稱查詢相關資料",
    options=[
        interactions.Option(
            name="card_id",
            description="根據卡號查詢",

        )
    ]
)
async def card_find(ctx: interactions.CommandContext):



bot.start()
