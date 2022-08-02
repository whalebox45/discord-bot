@bot.command()
async def kill(ctx):
    await ctx.send('bye')
    exit(1)
