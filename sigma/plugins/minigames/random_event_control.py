import discord
import yaml
import random

events_active = []


async def random_event_control(ev, message, args):
   
    if not message.guild: return

    events_enabled = ev.db.get_settings(message.guild.id, 'RandomEvents')
    if not events_enabled: return

    global events_active        
    event_id = message.guild.id + message.author.id
    if event_id in events_active: return

    chance = ev.db.get_settings(message.guild.id, 'EventChance')
    rolled_number = random.randint(1, 100)
    
    if rolled_number <= chance:
        with open(ev.resource('events.yml')) as events_file:
            event_data = yaml.safe_load(events_file)
                
        event = random.choice(event_data['events'])
        event_embed = discord.Embed(color=0x1abc9c, title='💠 An event!')
        choice_text_out = ''
        n = 0
        
        for choice in event['choices']:
            n += 1
            choice_text_out += '\n' + str(n) + ': ' + choice['choice_text']
        
        event_embed.add_field(name=event['event_text'], value=choice_text_out)
        event_embed.set_footer(text='Answer by inputting the number corresponding to your choice.')
        event_start = await message.channel.send('Hey ' + message.author.mention + '! An event has appeared!', embed=event_embed)
        events_active.append(event_id)
        
        try: 
            reply = await ev.bot.wait_for(event='message', check=lambda m: m.author == message.author ,timeout=10)
            
            try: await event_start.delete()
            except: pass

            try: await reply.delete()
            except: pass

        except Exception:
            out = discord.Embed(title=':clock10: Sorry, you timed out...', color=0x777777)
            await message.channel.send(None, embed=out)
            
            try: await event_start.delete()
            except: pass
            return
                

        try: answer_number = int(reply.content) - 1
        except: 
            out = discord.Embed(title=':exclamation: Sorry, I couldn\'t read that...', color=0xDB0000)
            await message.channel.send(None, embed=out)
            try: await event_start.delete()
            except: pass
            return
        
        if answer_number < 0 or answer_number > len(event['choices']) - 1:
            out = discord.Embed(title=':exclamation: Invalid number input', color=0xDB0000)
            await message.channel.send(None, embed=out)
            events_active.remove(event_id)
            try: await event_start.delete()
            except: pass
            return

        result = event['choices'][answer_number]
        choice_text = result['choice_text']
        positive = result['positive']
        point_amount = result['points']
        result_text = result['result_text']
        result_embed = discord.Embed(color=0x1abc9c, title='You chose to ' + choice_text.lower())
        
        try: await event_start.delete()
        except: pass
                
        if positive:
            ev.db.add_points(message.guild, message.author, point_amount)
            result_embed.set_footer(text='You have been awarded ' + str(point_amount) + ' points.')
        else:
            ev.db.take_points(message.guild, message.author, point_amount)
            result_embed.set_footer(text='You lost ' + str(point_amount) + ' points.')
        
        events_active.remove(event_id)
        result_embed.add_field(name='The following happened', value=result_text)
        await message.channel.send(None, embed=result_embed)