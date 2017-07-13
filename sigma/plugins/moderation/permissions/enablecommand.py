import discord
from sigma.core.permission import check_admin
from .nodes.permission_data import get_all_perms

async def enablecommand(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help()); 
        return

    if not check_admin(message.author, message.channel):
        response = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
        await message.channel.send(embed=response)
        return

    cmd_name = args[0].lower()
    if cmd_name in cmd.bot.alts:
        cmd_name = cmd.bot.alts[cmd_name]

    if cmd_name not in cmd.bot.plugin_manager.commands:
        response = discord.Embed(color=0x696969, title='🔍 Command Not Found')
        await message.channel.send(embed=response)
        return

    perms = get_all_perms(cmd.db, message)
    disabled_commands = perms['DisabledCommands']
    
    if cmd_name not in disabled_commands:
        response = discord.Embed(color=0xFF9900, title='⚠ Command Not Disabled')
        await message.channel.send(embed=response)
        return
              
    disabled_commands.remove(cmd_name)
    perms.update({'DisabledCommands': disabled_commands})
    cmd.db.update_one('Permissions', {'ServerID': message.guild.id}, {'$set': perms})

    response = discord.Embed(color=0x66CC66, title=f'✅ `{cmd_name.upper()}` enabled.')
    await message.channel.send(embed=response)
