import html
from msilib.schema import Component
import os
from pydoc import describe
from dotenv import load_dotenv

import interactions
import requests
from bs4 import BeautifulSoup

import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = interactions.Client(token=TOKEN)

@interactions.autodefer(delay=20)
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
    await ctx.send(str(value[0])+'\n```\n'+str(b)+'\n```')




@bot.command(name='my_deck')
async def my_deck(ctx: interactions.CommandContext):
    pass

@my_deck.subcommand(name="list",description="檢視在機器人上已儲存的牌組")
async def listdeck(ctx: interactions.CommandContext):
    await ctx.send('list my_deck')





@my_deck.subcommand(name='create',description="輸入ydk內容以建立牌組")
async def createdeck(ctx: interactions.CommandContext):
    test = 1
    if test > 2:
        await ctx.send("你已儲存太多的牌組了")
    else:
        decktitle = interactions.TextInput(
            style=interactions.TextStyleType.SHORT,
            label='牌組名稱',
            custom_id='ydk_title',
            min_length=0,
            max_length=64,
            required=False
        )
        deckinput = interactions.TextInput(
            style=interactions.TextStyleType.PARAGRAPH,
            label='輸入ydk資料內容',
            custom_id='ydk_data',
            min_length=1,
            max_length=1000,
        )
        modal = interactions.Modal(
            title="input",
            custom_id='makedeck_form',
            components=[decktitle,deckinput]
        )
        await ctx.popup(modal)






@bot.modal("makedeck_form")
async def makedeck_response(ctx: interactions.CommandContext,ydk_title: str, ydk_data:str):

    def deck_data(data):
        return 0


    deck_data(ydk_data)

    ebd = interactions.Embed(
        title=ydk_title,
        fields=[interactions.EmbedField(
            name='牌組',
            value=ydk_data,
            inline=True,
        )]
    )

    await ctx.send("這是你建立的牌組",embeds=ebd)




    print(ydk_title)
    print(ydk_data)


@my_deck.subcommand(name='modify')
async def updatedeck(ctx: interactions.CommandContext):
    await ctx.send('update my_deck')

@my_deck.subcommand(name='delete')
async def deletedeck(ctx: interactions.CommandContext):
    await ctx.send('delete my_deck')


@bot.command()
async def kill(ctx):
    await ctx.send('bye')
    exit(1)

bot.start()
