import aiohttp
import discord

from config import MashapeKey


async def hearthstone(cmd, message, args):

    hs_input = ' '.join(args).strip()
    if hs_input == '': await message.channel.send(cmd.help()); return

    url = 'https://omgvamp-hearthstone-v1.p.mashape.com/cards/search/' + hs_input + '?locale=enUS'
    headers = {'X-Mashape-Key': MashapeKey, 'Accept': 'text/plain'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as data:
            response = await data.json()
    
    if str(response).find("Bad Request") != -1:
        cmd.log.error("Bad Request")
        await message.channel.send('Something just went wrong! Contact the bot owner.')
        return

    if str(response).find("Missing Mashape application key") != -1:
        cmd.log.error("Invalid Mashape key")
        await message.channel.send('Something just went wrong! Contact the bot owner.')
        return

    card_list = '```'

    if len(response) > 1:
        n = 0
        for card in response:
            n += 1
            card_list += ('\n#' + str(n) + ': ' + card['name'])
            
        try:
            selector = await cmd.bot.send_message(message.channel, card_list + '\n```\nPlease type the number corresponding to the card of your choice `(1 - ' + str(len(response)) + ')`')
            choice = await cmd.bot.wait_for(event='message', check=lambda m: m.author == message.author ,timeout=20)
                
            try: await cmd.bot.delete(selector)
            except: pass
                
            try: card_no = int(choice.content) - 1
            except:
                await message.channel.send('Not a number or timed out... Please start over')
                return

            if choice is None: return
            
        except:
            await message.channel.send('The list is way too big, please be more specific...')
            return
        
    else: card_no = 0
    
    try:
        card_name = response[card_no]['name']
        card_img_url = response[card_no]['img']
        embed = discord.Embed(title=card_name, color=0x1ABC9C)
        embed.set_image(url=card_img_url)

        try: flavor_text = response[card_no]['flavor']
        except:
            flavor_text = None
        
        if flavor_text:
            flavor_out = '```\n' + flavor_text + '\n```'
            embed.add_field(name='Info', value=flavor_out)
    
        await message.channel.send(None, embed=embed)
    
    except:
        try:
            error = str(response['error'])
            err_message = str(response['message'])
            await message.channel.send('Error: ' + error + '.\n' + err_message)
    
        except Exception as e:
            cmd.log.error(e)
            await message.channel.send('Something went wrong...')
