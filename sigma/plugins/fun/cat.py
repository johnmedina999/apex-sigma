import aiohttp
import discord

async def cat(cmd, message, args):

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.thecatapi.com/v1/images/search') as data:
            results = await data.json()

    image_url = results[0]['url']
    embed = discord.Embed(color=0x1abc9c)
    embed.set_image(url=image_url)
    await message.channel.send(None, embed=embed)
