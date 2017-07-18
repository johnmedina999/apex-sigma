import os
import aiohttp
import nhentai
import discord
from PIL import Image
from io import BytesIO


async def hentai(cmd, message, args):
    
    search = ' '.join(args)
    if search == '': await message.channel.send(cmd.help()); return

    try:
        n = 0
        list_text = '```'

        entries = nhentai.search(search)['result']
        if len(entries) <= 1: nh_no = 0
        else:
            for entry in entries:
                n += 1
                list_text += '\n#' + str(n) + ' ' + entry['title']['pretty']

            try: list_message = await message.channel.send(list_text + '\n```\nPlease type the number corresponding to the anime of your choice `(1 - ' + str(len(entries)) + ')`')
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
            
            try: nh_no = int(choice.content) - 1
            except:
                await cmd.bot.send_message(message.channel, 'Not a number or timed out... Please start over')
                return

        try: nh_no = int(choice.content) - 1
        except: await message.channel.send('Invalid choice... Please start over'); return
        
        if nh_no < 0 or nh_no > len(entries) - 1:
            await message.channel.send('Invalid choice... Please start over'); return       

        hen_name = entries[nh_no]['title']['pretty']
        hen_id = entries[nh_no]['id']
        hen_media_id = entries[nh_no]['media_id']
        hen_url = ('https://nhentai.net/g/' + str(hen_id) + '/')
        hen_img = ('https://i.nhentai.net/galleries/' + str(hen_media_id) + '/1.jpg')
        nhen_text = ''
        
        async with aiohttp.ClientSession() as session:
            async with session.get(hen_img) as data:
                nh_cover_raw = await data.read()
            
        nh_cover_res = Image.open(BytesIO(nh_cover_raw))
        nh_cover = nh_cover_res.resize((251, 321), Image.ANTIALIAS)

        base = Image.open(cmd.resource('img/base.png'))
        overlay = Image.open(cmd.resource('img/overlay_nh.png'))

        base.paste(nh_cover, (100, 0))
        base.paste(overlay, (0, 0), overlay)
        base.save('cache/nh_' + str(message.author.id) + '.png')

        for tags in entries[nh_no]['tags']:
            nhen_text += '[' + str(tags['name']).title() + '] '
            
        await message.channel.send(file=discord.File('cache/nh_' + str(message.author.id) + '.png'))
        await message.channel.send('Name:\n```\n' + hen_name + '\n```\nTags:\n```\n' + nhen_text + '\n```\nBook URL: <' + hen_url + '>')
        os.remove('cache/nh_' + str(message.author.id) + '.png')

    except nhentai.nhentai.nHentaiException as e:
        await message.channel.send(e)
