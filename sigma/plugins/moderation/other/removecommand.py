import discord
from sigma.core.permission import check_man_srv


async def removecommand(cmd, message, args):
    
    if not check_man_srv(message.author, message.channel):
        response = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
        await message.channel.send(embed=response)
        return    

    if not args:
        response = discord.Embed(title='❗ Nothing Was Inputted', color=0xDB0000)
        await message.channel.send(embed=response)
        return

    trigger = args[0].lower()
    trigger_found = trigger in cmd.bot.plugin_manager.commands or trigger in cmd.bot.alts
    if trigger_found:
        response = discord.Embed(title='❗ Can\'t moify an existing core command', color=0xDB0000)
        await message.channel.send(embed=response)
        return
              
    try: custom_commands = cmd.db.get_settings(message.guild.id, 'CustomCommands')
    except:
        cmd.db.set_settings(message.guild.id, 'CustomCommands', {})
        custom_commands = {}
   
    del custom_commands[trigger]
    cmd.db.set_settings(message.guild.id, 'CustomCommands', custom_commands)
    
    response = discord.Embed(title=f'✅ {trigger} has been removed', color=0x66CC66)    
    await message.channel.send(embed=response)
