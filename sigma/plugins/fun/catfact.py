import aiohttp
import discord
import json


async def catfact(cmd, message, args):
        
        resource = 'http://catfacts-api.appspot.com/api/facts'
        async with aiohttp.ClientSession() as session:
            async with session.get(resource) as data:
                data = await data.read()
                data = json.loads(data)
        
        embed = discord.Embed(color=0x1abc9c)
        embed.add_field(name=':cat: Did you know...', value='```\n' + data['facts'][0] + '\n```')
        await message.channel.send(None, embed=embed)
