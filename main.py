import os
from dotenv import load_dotenv

import interactions
import requests
from bs4 import BeautifulSoup

import re
import base64

import sqlite3
import psycopg2



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_URL = os.getenv('DATABASE_URL')

CARD_DB_LOCATION = "decks/card.db"

bot = interactions.Client(token=TOKEN)

# 各個牌組區的最大張數
MAINDECK_MAX = 60
EXTRADECK_MAX = 15
SIDEDECK_MAX = 15

# 從ydk檔抓取表頭、牌組區名稱、張數限制
DECK_DICT = {
    'main':{
        'attr': '#main',
        'maxcard': MAINDECK_MAX,
        'name': "主牌組"},
    'extra':{
        'attr': '#extra',
        'maxcard': EXTRADECK_MAX,
        'name': "額外牌組"},
    'side':{
        'attr': '!side',
        'maxcard': SIDEDECK_MAX,
        'name': "備用牌組"}
}


@interactions.autodefer(delay=20)
@bot.command(
    name="win_deck",
    description="顯示每周台大卡牌研究社遊戲王上位餅圖與比例"
)
async def win_deck(ctx: interactions.CommandContext):
    

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
    
    await ctx.send("請問你要選哪一個時段的上位餅圖？")
    await ctx.send('```\n'+option_str+'\n```',components=week_menu)

@bot.component("week_select")
async def week(ctx, value):


    # 抓取網頁中的餅圖
    webdata = requests.get(value[0])
    soup = BeautifulSoup(webdata.text, "html.parser")
    sel = soup.find("div",{'class':'post'})
    await ctx.send(sel.find_next('img')["src"])
    

    # 尋找含有百分比符號的字串
    sel = soup.find_all('b')
    regex = re.compile("^.*[0-9](\s|)[0-9]+\.[0-9]\%.*")
    b = ""
    for s in sel:
        rs = regex.search(s.text)
        if rs is not None:
            b+=str(rs.group(0)) + '\n'
    await ctx.send(str(value[0])+'\n```\n'+str(b)+'\n```')


def get_deck_display_str(decktype: dict, deck_data: str):

    data_list = deck_data.splitlines()

    conn = sqlite3.connect(CARD_DB_LOCATION)
    output_str = ''
    # 從表頭區判斷資料行號，抓取最大數量以內的卡牌密碼
    
    card_bucket = {}

    for x in range(
        data_list.index(decktype['attr']) + 1,
        data_list.index(decktype['attr']) + decktype['maxcard'] +  1):
        
        # 當遇到非數字則忽略、表頭符號則結束
        if '#' in data_list[x] or '!' in data_list[x]: break
        elif not data_list[x].isnumeric(): continue

        if data_list[x] not in card_bucket:
            card_bucket[data_list[x]] = 1
        else:
            card_bucket[data_list[x]] += 1

    card_bucket = dict(sorted(card_bucket.items()))

    for cid in card_bucket:
        # 從資料庫查找卡名
        cur = conn.cursor()
        cur.execute("select CardName from Cards \
            where Passcode=(?) limit 1",("%08d"%int(cid),))
        fetch = cur.fetchone()

        cardname = "??"

        if fetch != None: cardname = str(fetch[0])

        # 串接連續字串
        output_str += f'{"%08d"%int(cid)}: {cardname} * {card_bucket[cid]}\n'
    
    
    conn.close()
    #回傳連續字串
    return output_str






@bot.command(name='my_deck')
async def my_deck(ctx: interactions.CommandContext):
    pass

@my_deck.subcommand(name="list",description="檢視在機器人上已儲存的牌組(Beta)")
async def listdeck(ctx: interactions.CommandContext):

    class DeckEmptyError(Exception):
        pass

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    cur.execute("""select id, user_id, deck_name from userdeck where user_id = %s ;""",(int(ctx.user.id),))
    try:
        fetch = cur.fetchall()
        conn.close()
        
        if not fetch: raise DeckEmptyError

        option_str = ""
        for i, x in enumerate(fetch):
            option_str += str(i+1) + ': ' + str(x[2]) + '\n'

        deck_menu = interactions.SelectMenu(
            options=[
                interactions.SelectOption(
                    label= str(i+1) + ': ' + str(x[2]),
                    value=x[0],
                )
                for i, x in enumerate(fetch)
            ],
            custom_id="deck_select"
        )

        await ctx.send('請選擇已儲存的牌組')
        await ctx.send('```\n'+option_str+'\n```', components=deck_menu)
    except DeckEmptyError:
        await ctx.send('你沒有存任何牌組喔')

@bot.component("deck_select")
async def deck_select(ctx, value):
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    cur.execute(""" select id, deck_data, deck_name from userdeck where id = %s ;""",(str(value[0]),))
    fetch = cur.fetchone()

    conn.close()

    print(fetch)

    b64_deck_bytes = fetch[1].encode('ascii')
    load_data_bytes = base64.b64decode(b64_deck_bytes)
    load_data = load_data_bytes.decode('ascii')

    ydk_title = fetch[2]

    embed_content = [interactions.EmbedField(
        name = DECK_DICT[d]['name'],
        value = get_deck_display_str(DECK_DICT[d],load_data),
        inline = False,
    ) for d in DECK_DICT]


    ebd = interactions.Embed(
        title=ydk_title,
        fields=embed_content,
    )

    await ctx.send(content="這是你所要檢視的牌組",embeds=ebd)



@my_deck.subcommand(name='create',description="輸入ydk內容以建立牌組(Beta)")
async def createdeck(ctx: interactions.CommandContext):

    class DeckOutOfLimitError(Exception):
        pass

    MAX_DECK_COUNT = 5

    conn = psycopg2.connect(DB_URL)

    cur = conn.cursor()

    
    cur.execute("""select count(*) from userdeck where user_id = %s """,(int(ctx.user.id),))
    
    fetch = cur.fetchone()
    conn.close()

    deck_count = fetch[0]
    
    try:
        if deck_count > MAX_DECK_COUNT: raise DeckOutOfLimitError
            
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
    except DeckOutOfLimitError:
        print("too many decks")
        await ctx.send("你已儲存太多的牌組了",ephemeral=True)

btn_nosave = interactions.Button(
    style=interactions.ButtonStyle.SECONDARY,
    label='否',
    custom_id="nosavedeck",
)
btn_save = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="是",
    custom_id="savedeck",
)


@bot.modal("makedeck_form")
async def makedeck_response(ctx: interactions.CommandContext,ydk_title: str, ydk_data:str):

    if ydk_title == "": ydk_title = "Unnamed"
            
    data_list = ydk_data.splitlines()
    
    @bot.component(btn_save)
    async def savedeck_res(ctx: interactions.CommandContext):
        

        save_data = ''

        maker_header = "#created by " + str(ctx.user.id)

        save_data += maker_header

        for d in DECK_DICT:
            save_data += '\n'
            decktype = DECK_DICT[d]

            save_data += decktype['attr'] 

            for x in range(data_list.index(decktype['attr']) + 1,data_list.index(decktype['attr']) + decktype['maxcard'] +  1):
                
                save_data += '\n'

                # 當遇到非數字則忽略、表頭符號則結束
                if '#' in data_list[x] or '!' in data_list[x]: break
                elif not data_list[x].isnumeric(): continue

                # 串接連續字串
                save_data += f'{data_list[x]}'
            

        save_data_bytes = save_data.encode('ascii')
        b64_bytes = base64.b64encode(save_data_bytes)
        b64_deck = b64_bytes.decode('ascii')

        conn = psycopg2.connect(DB_URL)

        cur = conn.cursor()

        
        cur.execute("""insert into userdeck(user_id,deck_name,deck_data) values(%s,%s,%s);""",
        (int(ctx.user.id),ydk_title,b64_deck))
        conn.commit()

        conn.close()

        # print(save_data)
        # print(b64_deck)
        

        await ctx.edit(components=interactions.ActionRow(
            components=[
            interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label='否',
                custom_id="nosavedeck",
                disabled=True,
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="是",
                custom_id="savedeck",
                disabled=True,
            ),]
        ))

        await ctx.send('牌組已儲存')
        



    @bot.component(btn_nosave)
    async def nosavedeck_res(ctx):

        await ctx.edit(components=interactions.ActionRow(
            components=[
            interactions.Button(
                style=interactions.ButtonStyle.SECONDARY,
                label='否',
                custom_id="nosavedeck",
                disabled=True,
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label="是",
                custom_id="savedeck",
                disabled=True,
            ),]
        ))
        await ctx.send('已取消儲存')
        

    embed_content = [interactions.EmbedField(
        name = DECK_DICT[d]['name'],
        value = get_deck_display_str(DECK_DICT[d],ydk_data),
        inline = False,
    ) for d in DECK_DICT]


    ebd = interactions.Embed(
        title=ydk_title,
        fields=embed_content,
    )
 
    btn_row = interactions.ActionRow(components=[btn_nosave,btn_save])

    await ctx.send(content="這是你建立的牌組，請問要儲存嗎？",embeds=ebd,components=btn_row, ephemeral=True)




@my_deck.subcommand(name='delete')
async def deletedeck(ctx: interactions.CommandContext):
    await ctx.send('還沒寫，欲刪除請洽機器人作者')
    

bot.start()
