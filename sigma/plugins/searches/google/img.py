import aiohttp
import random
import discord
from config import GoogleAPIKey
from config import GoogleCSECX


async def img(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help())
        return

    if (GoogleAPIKey == '') or (GoogleCSECX == ''):
        embed = discord.Embed(color=0xDB0000)
        embed.add_field(name='API key GoogleAPIKey and/or GoogleCSECX not found.', value='Please ask the bot owner to add them.')
        await message.channel.send(None, embed=embed)
        return

    search = ' '.join(args)
    url = 'https://www.googleapis.com/customsearch/v1?q=' + search + '&cx=' + GoogleCSECX + '&searchType=image&safe=high' + '&key=' + GoogleAPIKey
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as data:
            results = await data.json()
        
    try:
        result_items = results['items']
        choice = random.choice(result_items)
        title = choice['title']
        if len(title) > 48:
            title = title[:48] + '...'
        url = choice['link']
        
        embed = discord.Embed(color=0x1abc9c, title=title)
        embed.set_image(url=url)
        await message.channel.send(None, embed=embed)
    except:
        embed = discord.Embed(color=0xDB0000, title='❗ Daily Limit Reached.')
        embed.set_footer(text='Google limits this API feature, and we hit that limit.')
        await message.channel.send(None, embed=embed)
