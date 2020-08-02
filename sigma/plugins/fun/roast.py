import random
import aiohttp
import discord
from bs4 import BeautifulSoup

async def roast(cmd, message, args):

    target = message.author if not message.mentions else message.mentions[0]

    page_num = random.randint(1, 30)
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://onelinefun.com/insults/{page_num}/') as data:
            page = await data.text()

    root = BeautifulSoup(page, 'html.parser')
    content = [str(i)[3:-4] for i in root.find_all('p')[:-3]]
        # str(i) for converting tag type into string
        # [3:-4] for cutting out the <p></p> tags
        # [:-3] because there are always 3 lines that are <p> tags but not roasts

    if len(content) != 10:
        cmd.log.error(f'Error parsing http://onelinefun.com/insults/{page_num}/')
        embed = discord.Embed(color=0xDB0000, title='Something went wrong. Notify bot owner.')
        await message.channel.send(None, embed=embed)
        return

    embed = discord.Embed(color=0xCC6666)
    embed.add_field(name=':fire::fire::fire::fire::fire::fire:', value=f'<@{target.id}> {random.choice(content)} ')
    await message.channel.send(None, embed=embed)
