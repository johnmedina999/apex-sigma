import aiohttp
import discord
from config import MashapeKey


async def tagdef(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help())
        return

    if MashapeKey == '':
        embed = discord.Embed(color=0xDB0000)
        embed.add_field(name='API key MashapeKey not found.', value='Please ask the bot owner to add it.')
        await message.channel.send(None, embed=embed)
        return

    hashtag = (' '.join(args)).replace('#', '')
    url = "https://tagdef.p.mashape.com/one." + hashtag + '.json'
    headers = {'X-Mashape-Key': MashapeKey, 'Accept': 'text/plain'}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as data:
            response = await data.json()
    
    result = response['defs']['def']['text']
    
    embed = discord.Embed(color=0x1abc9c)
    embed.add_field(name='#⃣ Definition of `#' + hashtag + '`', value='```\n' + result + '\n```')
    await message.channel.send(None, embed=embed)
