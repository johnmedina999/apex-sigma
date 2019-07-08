import random
import aiohttp
import discord
from bs4 import BeautifulSoup

async def roast(cmd, message, args):

    if message.mentions: target = message.mentions[0]
    else: target = message.author

    page_num = random.randint(0, 36)
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://onelinefun.com/insults/{page_num}/') as data:
            page = await data.text()

    root = BeautifulSoup(page, 'html.parser')
    roast_html = root.find_all(class_='oneliner')

    if len(roast_html) != 10:
        cmd.log.error(f'Error parsing http://onelinefun.com/insults/{page_num}/')
        embed = discord.Embed(color=0xDB0000, title='Something went wrong. Notify bot owner.')
        await message.channel.send(None, embed=embed)
        return

    roast_choose = random.randint(0, 9)
    roast_text = roast_html[roast_choose].find('p').text

    embed = discord.Embed(color=0xCC6666)
    embed.add_field(name=':fire::fire::fire::fire::fire::fire:', value=f'<@%s> {roast_text} ' % target.id)
    await message.channel.send(None, embed=embed)
