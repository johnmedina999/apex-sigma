﻿from sigma.core.permission import check_man_roles
from sigma.core.rolecheck import matching_role
import discord


async def addselfrole(cmd, message, args):
    
    if not check_man_roles(message.author, message.channel):
        out_content = discord.Embed(type='rich', color=0xDB0000, title='⛔ Insufficient Permissions. Server Admin Only.')
        await message.channel.send(None, embed=out_content)
        return
    
    if not args:
        out_content = discord.Embed(type='rich', color=0xDB0000, title='❗ Error')
        out_content.add_field(name='Not Enough Arguments', value=cmd.help())
        await message.channel.send(None, embed=out_content)
        return
    
    role_qry = ' '.join(args)
    target_role = matching_role(message.guild, role_qry)
    
    if not target_role:
        out_content = discord.Embed(type='rich', color=0xFF9900, title='❗ Error')
        out_content.add_field(name='Role Not Found', value='I was unable to find **' + role_qry + '** on this server.')
        await message.channel.send(None, embed=out_content)
        return

    try: self_roles = cmd.db.get_settings(str(message.guild.id), 'SelfRoles')
    except:
        cmd.db.set_settings(str(message.guild.id), 'SelfRoles', [])
        self_roles = []
        
    if target_role.id in self_roles or target_role.name in self_roles:
        out_content = discord.Embed(type='rich', color=0xFF9900, title='⚠ Error')
        out_content.add_field(name='Role In List', value='The role **' + role_qry + '** is already in the list of self assignable roles.')
        await message.channel.send(None, embed=out_content)
        return

    self_roles.append(target_role.id)
    cmd.db.set_settings(str(message.guild.id), 'SelfRoles', self_roles)
        
    out_content = discord.Embed(type='rich', color=0x66cc66, title='✅ Role **' + target_role.name + '** added to the self assignable roles list.')
    await message.channel.send(None, embed=out_content)