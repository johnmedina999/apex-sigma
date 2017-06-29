import os
import aiohttp
import discord
from lxml import html
from io import BytesIO
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from config import MALUserName, MALPassword


async def anime(cmd, message, args):
    list_message = None
    choice = None

    mal_input = ''.join(args).strip()
    if mal_input == '': await message.channel.send(cmd.help()); return
    
    mal_url = 'https://myanimelist.net/api/anime/search.xml?q=' + mal_input
    async with aiohttp.ClientSession() as session:
        async with session.get(mal_url, auth=aiohttp.BasicAuth(MALUserName, MALPassword)) as data:
            mal = await data.read()
    
    if str(mal) == "b''":
        await message.channel.send('Search found nothing :slight_frown: ')
        return

    if str(mal).find("Invalid credentials") != -1:
        cmd.log.error("Invalid MAL credentials")
        await message.channel.send('Something just went wrong! Contact the bot owner.')
        return

    n = 0
    entries = html.fromstring(mal)
    list_text = 'List of anime found for `' + mal_input + '`:\n```'

    if len(entries) <= 1: ani_no = 0
    else:
        for entry in entries:
            n += 1
            list_text += '\n#' + str(n) + ' ' + entry[1].text

        try: list_message = await message.channel.send(list_text + '\n```\nPlease type the number corresponding to the anime of your choice `(1 - ' + str(len(entries)) + ')`')
        except: await message.channel.send('The list is way too big, please be more specific...'); return
        
        choice = await cmd.bot.wait_for(event='message', check=lambda m: m.author == message.author ,timeout=20)
        if choice is None: await message.channel.send('timed out... Please start over'); return

        try: ani_no = int(choice.content) - 1
        except: await message.channel.send('Not a number or timed out... Please start over'); return
        
        if ani_no < 0 or ani_no > len(entries) - 1:
            await message.channel.send('Invalid choice'); return        
    
    try:
        try: await cmd.bot.delete(list_message)
        except: pass
    
        try: await cmd.bot.delete(choice)
        except: pass
        
        with message.channel.typing(): pass
       
        ani_id = entries[ani_no][0].text
        name = entries[ani_no][1].text
        eps = entries[ani_no][4].text
        score = entries[ani_no][5].text

        air_start = entries[ani_no][8].text
        if air_start == '0000-00-00': air_start = '???'

        air_end = entries[ani_no][9].text
        if air_end == '0000-00-00': air_end = '???'
        
        air = air_start.replace('-', '.') + ' to ' + air_end.replace('-', '.')
        
        try: synopsis = entries[ani_no][10].text.replace('[i]', '').replace('[/i]', '').replace('<br>', '').replace('</br>', '').replace('<br />', '').replace('&#039;', '\'').replace('&quot;', '"').replace('&mdash;', '-')
        except: synopsis = 'None'

        img = entries[ani_no][11].text
        ani_type = entries[ani_no][6].text
        status = entries[ani_no][7].text

        if len(name) > 22: suffix = '...'
        else: suffix = ''

        async with aiohttp.ClientSession() as session:
            async with session.get(img) as data:
                ani_img_raw = await data.read()
        
        try: ani_img = Image.open(BytesIO(ani_img_raw))
        except: cmd.log.error("Could not open raw image"); raise

        try: base = Image.open(cmd.resource('img/base.png'))
        except: cmd.log.error("Could not open img/base.png"); raise

        try: overlay = Image.open(cmd.resource('img/overlay_anime.png')); 
        except: cmd.log.error("Could not open img/overlay_anime.png"); raise
        
        base.paste(ani_img, (0, 0))
        base.paste(overlay, (0, 0), overlay)

        try: font = ImageFont.truetype(cmd.resource('fonts/big_noodle_titling_oblique.ttf'), 28)
        except: cmd.log.error("Could not open big_noodle_titling_oblique.ttf"); raise

        imgdraw = ImageDraw.Draw(base)
        imgdraw.text((4, 4), '#' + ani_id, (255, 255, 255), font=font)
        imgdraw.text((227, 16), name[:21] + suffix, (255, 255, 255), font=font)
        imgdraw.text((227, 110), 'Type: ' + ani_type, (255, 255, 255), font=font)
        imgdraw.text((227, 138), 'Status: ' + status, (255, 255, 255), font=font)
        imgdraw.text((227, 166), 'Episodes: ' + eps, (255, 255, 255), font=font)
        imgdraw.text((227, 194), 'Score: ' + score, (255, 255, 255), font=font)
        imgdraw.text((227, 222), air, (255, 255, 255), font=font)
        base.save('cache/anime_' + str(message.author.id) + '.png')

        await message.channel.send(file=discord.File('cache/anime_' + str(message.author.id) + '.png'))
        await message.channel.send('```\n' + synopsis[:256] + '...\n```\nMore at: <https://myanimelist.net/anime/' + ani_id + '/>\n')
        os.remove('cache/anime_' + str(message.author.id) + '.png')
    
    except IndexError: await message.channel.send('Number out of range, please start over...')
    except UnboundLocalError: pass
    except Exception as e:
        cmd.log.error(e)
        await message.channel.send('Not found or API dun goofed...')
