import discord
import aiohttp
import os
from PIL import Image
from io import BytesIO


async def rgby(cmd, message, args):
    args = [arg for arg in args if arg.strip() != '']

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    url = args[0]

    if len(args) > 1: force_width = int(args[1])
    else:             force_width = 32

    if len(args) > 2: exposure = int(args[2])
    else:             exposure = 100

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as data:
            try:
                image = Image.open(BytesIO(await data.read()))
            except:
                embed = discord.Embed(type='rich', color=0xDB0000, title='❗ Error: Not a link to a valid image')
                await message.channel.send(None, embed=embed)
                return        
    
    width, height = image.size
    image = image.resize((force_width, int(height*(float(force_width)/float(width)))), Image.ANTIALIAS)
    
    img_data = list(image.getdata())

    z_unicode = u'\U00003000'.encode('unicode-escape')
    r_unicode = u'🈵'.encode('unicode-escape')
    g_unicode = u'🈹'.encode('unicode-escape')
    b_unicode = u'🈳'.encode('unicode-escape')
    y_unicode = u'🈷️'.encode('unicode-escape')

    rgby = (z_unicode, r_unicode, g_unicode, y_unicode, b_unicode, '', '' , y_unicode)
    hor = 1
    text = '```'

    for pixel in img_data:
        if hor > force_width: hor = 1; text += '\n'
        r,g,b,a = pixel

        # If color is more than 127, make it 1, otherwise 0
        r = min(1, max((r - exposure), 0))
        g = min(1, max((g - exposure), 0))
        b = min(1, max((b - exposure), 0))

        '''
        1 = r
        2 = g
        3 = r + g = y
        4 = b
        5 = r + b = ?
        6 = g + b = ?
        7 = r + g + b = y
        '''
        color = r*1 + g*2 + b*4
        
        if color == 5: 
            if pixel[0] > pixel[2]: color = 1
            else:                   color = 4

        if color == 6:
            if pixel[1] > pixel[2]: color = 2
            else:                   color = 4

        if color == 5 or color == 6:
            print(color)


        text += rgby[color].decode('unicode-escape')
        hor += 1
        
    text += '```'

    try: await message.channel.send(text)
    except:
        embed = discord.Embed(type='rich', color=0xDB0000, title='❗ Error: Oops, too big! Try setting the width paramter after the link')
        await message.channel.send(None, embed=embed)
        return
    
