import discord
import aiohttp
from config import MashapeKey
from io import BytesIO


async def qrcode(cmd, message, args):
    
    if not args:
        await cmd.bot.send_message(message.channel, cmd.help())
        return

    if MashapeKey == '':
        embed = discord.Embed(color=0xDB0000)
        embed.add_field(name='API key MashapeKey not found.', value='Please ask the bot owner to add it.')
        await message.channel.send(None, embed=embed)
        return

    url = 'https://neutrinoapi-qr-code.p.mashape.com/qr-code'
    content = ' '.join(args)
    headers = {
        "X-Mashape-Key": MashapeKey,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    params = {
        "bg-color": "#FFFFFF",
        "content": content,
        "fg-color": "#000000",
        "height": 512,
        "width": 512
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params, headers=headers) as data:
            data = await data.read()
    
    output = discord.File(BytesIO(data), filename=f'qr_{message.id}.png')
    await message.channel.send(file=output)
    
    if args[-1].startswith('del'):
        try: await message.delete()
        except: pass
