import discord
from sigma.core.permission import check_admin
from .nodes.permission_data import get_all_perms


async def enablemodule(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help()); 
        return

    if not check_admin(message.author, message.channel):
        response = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
        await message.channel.send(cmd.help()); 
        return

    mdl_name = args[0].lower()

    if mdl_name not in cmd.bot.module_list:
        response = discord.Embed(color=0x696969, title='🔍 Module Not Found')
        await message.channel.send(cmd.help()); 
        return
        
    perms = get_all_perms(cmd.db, message)
    disabled_modules = perms['DisabledModules']

    if mdl_name not in disabled_modules:
        response = discord.Embed(color=0xFF9900, title='⚠ Module Not Disabled')
        await message.channel.send(cmd.help()); 
        return
                   
    disabled_modules.remove(mdl_name)
    perms.update({'DisabledModules': disabled_modules})
    cmd.db.update_one('Permissions', {'ServerID': message.guild.id}, {'$set': perms})
                    
    response = discord.Embed(color=0x66CC66, title=f'✅ `{mdl_name.upper()}` enabled.')                  
    await message.channel.send(embed=response)
