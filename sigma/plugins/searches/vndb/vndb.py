import os
import discord
import aiohttp
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO


async def vndb(cmd, message, args):

    vndb_input = ' '.join(args)
    if vndb_input == '': await message.channel.send(cmd.help()); return

    vndb_url =  'https://vndb.org/v/all?q=' + vndb_input + '&fil=tagspoil-0&rfil=&s=title&o=a'
    async with aiohttp.ClientSession() as session:
        async with session.get(vndb_url) as data:
            page = await data.read()

    root = BeautifulSoup(page, "html")
    entries = root.find_all(class_='tc1')
    
    n = 0
    list_text = 'List of VN found for `' + vndb_input + '`:\n```'


    if not entries or len(entries) <= 1:
        await message.channel.send('Search found nothing :slight_frown:')
        return

    if len(entries) <= 2: vn_no = 1      
    else:
        for entry in entries:
            n += 1
            if n == 1: continue # skip the header
            list_text += '\n#' + str(n - 1) + ' ' + entry.text

        try: list_message = await message.channel.send(list_text + '\n```')
        except: await message.channel.send('The list is way too big, please be more specific...'); return

        try: 
            choice = await cmd.bot.wait_for(event='message', check=lambda m: m.author == message.author ,timeout=20)
            
            try: await list_message.delete()
            except: pass

            try: await choice.delete()
            except: pass

        except Exception: 
            try: await list_message.delete()
            except: pass

            await message.channel.send('timed out... Please start over'); return

        try: vn_no = int(choice.content)
        except: await message.channel.send('Invalid choice... Please start over'); return

    if vn_no < 1 or vn_no > len(entries):
        await message.channel.send('Invalid choice... Please start over'); return        

    try: choice_url = entries[vn_no].find('a', href=True)['href']
    except: await message.channel.send('Something went wrong! Contact bot owner.'); return

    vndb_url =  'https://vndb.org' + choice_url
    async with aiohttp.ClientSession() as session:
        async with session.get(vndb_url) as data:
            page = await data.read()

    root = BeautifulSoup(page, "html")

    try:
        vn_title = root.find_all(class_='stripe')[0].find_all('td', string='Title')[0].nextSibling.text
        vn_img_url = root.find_all(class_='vnimg')[0].find('img')['src']
        vn_devs = root.find_all(class_='stripe')[0].find_all('td', string='Developer')[0].nextSibling.text
        vn_desc = root.find_all(class_='vndesc')[0].find('p').text
    except:
        await message.channel.send('Something went wrong! Contact bot owner.')
        return

    if len(vn_desc) > 1000: vn_desc = vn_desc[:1000] + "..."   

    async with aiohttp.ClientSession() as session:
        async with session.get(vn_img_url) as data:
            vn_cover_raw = await data.read()
    
    vn_cover_res = Image.open(BytesIO(vn_cover_raw))
    vn_cover = vn_cover_res.resize((231, 321), Image.ANTIALIAS)
    base = Image.open(cmd.resource('img/base_vn.png'))
    overlay = Image.open(cmd.resource('img/overlay_vn.png'))
    
    base.paste(vn_cover, (110, 0))
    base.paste(overlay, (0, 0), overlay)
    base.save('cache/vn_' + str(message.id) + '.png')

    await message.channel.send(file=discord.File('cache/vn_' + str(message.id) + '.png'))
    await message.channel.send('Title: `' + vn_title + '`\nDescription:```\n' + vn_desc + '\n```\nMore at: ' + vndb_url + '>')
    os.remove('cache/vn_' + str(message.id) + '.png')