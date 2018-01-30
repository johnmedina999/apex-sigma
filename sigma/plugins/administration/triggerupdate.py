import discord
from config import permitted_id
import subprocess


async def triggerupdate(cmd, message, args):
    if not message.author.id in permitted_id: return

    cmd.log.info('Update triggered by user {:s}'.format(message.author.name))

    status = discord.Embed(title=f':exclamation: {cmd.bot.user.name} Update triggered.', color=0x808000)
    try: await message.channel.send(None, embed=status)
    except: pass

    p = subprocess.Popen("git pull master master", shell=True, stdout=subprocess.PIPE)
    log = ''

    for line in p.stdout.readlines(): 
        line = line.decode('ascii')
        cmd.log.info(line)
        log += line

    retval = p.wait()

    if retval == 0:
        status = discord.Embed(title=f':white_check_mark:  Update Successful', color=0x008800)
        try: await message.channel.send(None, embed=status)
        except: pass

        status = discord.Embed(title=f':skull_crossbones: {cmd.bot.user.name} Shutting Down.', color=0x808080)
        try: await message.channel.send(None, embed=status)
        except: pass
    
        await cmd.bot.logout()
        await cmd.bot.close()
    else:
        status = discord.Embed(title=f':x: Update Failed', color=0x880000)
        try: await message.channel.send(None, embed=status)
        except: pass

        lst_out = [log[i:i+1500] for i in range(0, len(log), 1500)]
        for chunk in lst_out: await message.author.send('```'+ chunk + '```')
