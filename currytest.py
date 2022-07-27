import os
import asyncio

from dotenv import load_dotenv

import sqlite3

import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

conn = sqlite3.connect('memo.db')
cursor = conn.cursor()

bot = commands.Bot(command_prefix='/')

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def memo(ctx, arg):

    if arg =='add':
        await ctx.send(str(ctx.author) + " 你要寫些什麼？（50字以內）")

        def check(m):
            return (
                m.author == ctx.author and
                m.channel.id == ctx.channel.id
                )

        try:
            note = await bot.wait_for('message',timeout=300.0,check=check)
        except asyncio.TimeoutError:
            await ctx.send('太久了，先不幫你存了')
        except:
            await ctx.send('出了點狀況，沒辦法幫你存')
        else:
            await ctx.send("知道了，所以要幫你把這句話存下來嗎？(Y/n): "+ note.content)
            try: 
                msg = await bot.wait_for('message', timeout=30.0,check=check)
            except asyncio.TimeoutError:
                await ctx.send('太久了，先不幫你存了')
            except:
                await ctx.send('出了點狀況，沒辦法幫你存')
            else:
                if msg.content.lower() in ("y","yes"):
                    await ctx.send('那麼我就幫你把這句話存下來囉！')
                    print(",".join([str(note.author.id), str(note.channel.id), note.content]))
                    cursor.execute('insert into "main"."memo"(user_id,channel_id,note) values(?, ?, ?)',
                        (note.author.id, note.channel.id, note.content))
                    conn.commit()
                else:
                    await ctx.send('那我就不幫你存了')

        finally:
            del note, msg
    
    if arg == 'show':
        await ctx.send(str(ctx.author) + " 你好，這是你存過的備忘錄")

        cursor.execute('select note from "main"."memo" where user_id = ? and channel_id = ?',
            (ctx.author.id, ctx.channel.id))

        notelist = [x[0] for x in cursor.fetchall()]

        notestr = ''
        for index in range(len(notelist)):
            notestr += f'[{index+1:>{len(str(len(notelist)))}}] {notelist[index]}\n'

        embed = discord.Embed(title=" ")
        embed.add_field(name="備忘錄",value='`'+notestr+'`')

        await ctx.send(embed=embed)

    




bot.run(TOKEN)
