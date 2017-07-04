import aiohttp
import discord


async def ronswanson(cmd, message, args):
    
    api_url = 'http://ron-swanson-quotes.herokuapp.com/v2/quotes'
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as data:
            data = await data.json()
    
    joke = data[0]
    out = '```yaml\n\"' + joke + '\"\n```'
    
    embed = discord.Embed(color=0x1abc9c)
    embed.add_field(name='😠 Have a Ron Swanson Quote', value=out)
    await message.channel.send(None, embed=embed)
