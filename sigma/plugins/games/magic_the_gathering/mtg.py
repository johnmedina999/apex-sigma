import os
import aiohttp
import discord
from io import BytesIO
from PIL import Image
from humanfriendly.tables import format_pretty_table

async def mtg(cmd, message, args):
    
    q = ' '.join(args).strip()
    if q == '': await message.channel.send(cmd.help()); return

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.magicthegathering.io/v1/cards?name=' + q) as data:
            cards = await data.json()

    n = 0
    list_text = 'List of cards found for `' + str(q) + '`:\n```'
    
    column_names = ['no.', 'set', 'name']
    rows = []

    if len(cards['cards']) > 1:
        for entry in cards['cards']:
            n += 1
            rows.append([str(n), entry['set'], entry['name']])
        
        list_text = '```' + format_pretty_table(rows, column_names)
        selector = await message.channel.send(list_text + '\n```\nPlease type the number corresponding to the card of your choice `(1 - ' + str(len(cards['cards'])) + ')`')

        try: 
            choice = await cmd.bot.wait_for(event='message', check=lambda m: m.author == message.author, timeout=20)
        
            try: await selector.delete()
            except: pass

            try: await choice.delete()
            except: pass

        except Exception: 
            try: await selector.delete()
            except: pass

            await message.channel.send('timed out... Please start over'); return
            return

        try: card_no = int(choice.content) - 1
        except:
            await message.channel.send('Not a number... Please start over'); return

        if card_no < 0 or card_no > len(cards['cards']) - 1:
            await message.channel.send('Invalid choice'); return    

    else: card_no = 0

    if not 'imageUrl' in cards['cards'][card_no]:
        await message.channel.send('No available image for this card :slight_frown:'); return

    try:
        card_img_url = cards['cards'][card_no]['imageUrl']

        async with aiohttp.ClientSession() as session:
            async with session.get(card_img_url) as data:
                card_img_raw = await data.read()

        try: card_img = Image.open(BytesIO(card_img_raw))
        except: cmd.log.error("Could not open raw image"); raise

        card_img.save('cache/card_img_' + str(message.author.id) + '.png')
        await message.channel.send(file=discord.File('cache/card_img_' + str(message.author.id) + '.png'))
        os.remove('cache/card_img_' + str(message.author.id) + '.png')

    except Exception as e:
        cmd.log.error(e)
        await message.channel.send('I was not able to get the image for the selected card...')
        return