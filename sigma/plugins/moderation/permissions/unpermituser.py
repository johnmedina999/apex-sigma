import discord
from sigma.core.permission import check_admin
from .nodes.permission_data import get_all_perms, generate_cmd_data


async def unpermituser(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help()); 
        return

    if len(args) < 2:
        response = discord.Embed(color=0xDB0000, title='❗ Not Enough Arguments')
        await message.channel.send(embed=response)
        return

    if not check_admin(message.author, message.channel):
        response = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
        await message.channel.send(embed=response)
        return
        
    if not message.mentions:
        response = discord.Embed(color=0x696969, title=f'🔍 No User Targeted')
        await message.channel.send(embed=response)
        return
              
    target = message.mentions[0]
                    
    try: perm_mode, cmd_name = args[0].split(':')
    except:
        response = discord.Embed(color=0xDB0000, title='❗ Bad Input')
        await message.channel.send(embed=response)
        return
                    
    cmd_name = cmd_name.lower()
    perm_mode = perm_mode.lower()
    
    if perm_mode == 'c':
        exception_group = 'CommandExceptions'
        check_group = cmd.bot.plugin_manager.commands
        check_alts = True
    elif perm_mode == 'm':
        exception_group = 'ModuleExceptions'
        check_group = cmd.bot.module_list
        check_alts = False
    else:
        response = discord.Embed(color=0xDB0000, title='❗ Bad Input')
        await message.channel.send(embed=response)
        return

    if check_alts:
        if cmd_name in cmd.bot.alts:
            cmd_name = cmd.bot.alts[cmd_name]
                    
    if cmd_name not in check_group:
        response = discord.Embed(color=0x696969, title='🔍 Command/Module Not Found')
        await message.channel.send(embed=response)
        return
                        
    perms = get_all_perms(cmd.db, message)
    cmd_exc = perms[exception_group]
                        
    if cmd_name in perms[exception_group]:
        inner_exc = cmd_exc[cmd_name]
    else:
        inner_exc = generate_cmd_data(cmd_name)[cmd_name]
                        
    exc_usrs = inner_exc['Users']
                        
    if target.id not in exc_usrs:
        response = discord.Embed(color=0xFF9900, title=f'⚠ {target.name} is not able to use `{cmd_name}`')
        await message.channel.send(embed=response)
        return
                            
    exc_usrs.remove(target.id)
    inner_exc.update({'Users': exc_usrs})
    cmd_exc.update({cmd_name: inner_exc})
    perms.update({exception_group: cmd_exc})
    cmd.db.update_one('Permissions', {'ServerID': message.guild.id}, {'$set': perms})
    
    response = discord.Embed(color=0x66CC66, title=f'✅ `{target.name}` can no longer use `{cmd_name}`.')
    await message.channel.send(embed=response)
