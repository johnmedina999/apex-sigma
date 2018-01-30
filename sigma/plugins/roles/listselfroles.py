import discord


async def listselfroles(cmd, message, args):
    
    self_roles = cmd.db.get_settings(str(message.guild.id), 'SelfRoles')
    role_list = []
    
    for srv_role in message.guild.roles:
        for role in self_roles:
            if role == srv_role.id or role == srv_role.name:
                role_list.append(srv_role.name)
    
    if not role_list:
        embed = discord.Embed(type='rich', color=0x0099FF, title='ℹ No Self Assignable Roles Set')
        await message.channel.send(None, embed=embed)
        return

    role_list = sorted(role_list)
    rl_str = '\n- ' + '\n- '.join(role_list)
    rl_out = [ '\n'.join(rl_str.splitlines()[50*i:i*50+50]) for i in range(0, int(rl_str.count('\n')/50) + 1) ]

    for rl in rl_out:
        embed = discord.Embed(type='rich', color=0x1ABC9C)
        embed.add_field(name='Self Assignable Roles On ' + message.guild.name, value='```\n' + rl + '\n```')    
        await message.channel.send(None, embed=embed)
