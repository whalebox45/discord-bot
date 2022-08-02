import os

import json

import discord
from dotenv import load_dotenv

from discord.ext import commands

keyword_file = open('keyword.json','r',encoding="utf-8")
keyword_data = json.load(keyword_file)



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='/')

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def pasta(ctx, arg):
    for j in keyword_data['pasta']:
        if arg in j['keywords']:
            await ctx.send(j['value'])

bot.run(TOKEN)

