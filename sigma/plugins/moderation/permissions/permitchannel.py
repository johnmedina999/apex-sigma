import discord
from sigma.core.permission import check_admin
from .nodes.permission_data import get_all_perms, generate_cmd_data


async def permitchannel(cmd, message, args):
    if args:
        if len(args) >= 2:
            if not check_admin(message.author, message.channel):
                response = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
            else:
                if message.channel_mentions:
                    target = message.channel_mentions[0]
                    error_response = discord.Embed(color=0xDB0000, title='❗ Bad Input')
                    try:
                        perm_mode, cmd_name = args[0].split(':')
                    except:
                        await message.channel.send(embed=error_response)
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
                        await message.channel.send(embed=error_response)
                        return
                    if check_alts:
                        if cmd_name in cmd.bot.alts:
                            cmd_name = cmd.bot.alts[cmd_name]
                    if cmd_name in check_group:
                        perms = get_all_perms(cmd.db, message)
                        if cmd_name in perms[exception_group]:
                            cmd_exc = perms[exception_group]
                        else:
                            cmd_exc = generate_cmd_data(cmd_name)
                        inner_exc = cmd_exc[cmd_name]
                        exc_usrs = inner_exc['Channels']
                        if target.id in exc_usrs:
                            response = discord.Embed(color=0xFF9900,
                                                     title=f'⚠ #{target.name} can already use `{cmd_name}`')
                        else:
                            exc_usrs.append(target.id)
                            inner_exc.update({'Channels': exc_usrs})
                            cmd_exc.update({cmd_name: inner_exc})
                            perms.update({exception_group: cmd_exc})
                            cmd.db.update_one('Permissions', {'ServerID': message.guild.id}, {'$set': perms})
                            response = discord.Embed(color=0x66CC66,
                                                     title=f'✅ `#{target.name}` can now use `{cmd_name}`.')
                    else:
                        response = discord.Embed(color=0x696969, title='🔍 Command/Module Not Found')
                else:
                    response = discord.Embed(color=0x696969, title='🔍 No Channel Mentioned')
            await message.channel.send(embed=response)
