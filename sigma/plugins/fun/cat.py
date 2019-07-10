import aiohttp
from config import CatAPIKey
from lxml import html
import random
import discord


async def cat(cmd, message, args):

    if CatAPIKey == '':
        embed = discord.Embed(color=0xDB0000)
        embed.add_field(name='API key CatAPIKey not found.', value='Please ask the bot owner to add it.')
        await message.channel.send(None, embed=embed)
        return

    async with aiohttp.ClientSession() as session:
        async with session.get('http://thecatapi.com/api/images/get?format=xml&results_per_page=100&api_key=' + CatAPIKey) as raw_page:
            results = html.fromstring(await raw_page.text())[0][0]

    choice = random.choice(results)
    image_url = str(choice[0].text)

    embed = discord.Embed(color=0x1abc9c)
    embed.set_image(url=image_url)
    await message.channel.send(None, embed=embed)
