import discord


async def inrole(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help())
        return
    
    role_input = ' '.join(args)
    role_choice = None
    user_list = []
    
    for role in message.guild.roles:
        if role.name.lower() == role_input.lower():
            role_choice = role
    
    if not role_choice:
        embed = discord.Embed(color=0x696969, title=':notebook: No role like that was found on this server.')
        await message.channel.send(None, embed=embed)
        return

    for member in message.guild.members:
        for role in member.roles:
            if role == role_choice:
                user_list.append(member.name)


    user_list = sorted(user_list)
    lst_str = '\n- ' + '\n- '.join(user_list)
    lst_out = [ '\n'.join(lst_str.splitlines()[50*i:i*50+50]) for i in range(0, int(lst_str.count('\n')/50) + 1) ]

    for usr in lst_out:
        embed = discord.Embed(color=0x0099FF)
        embed.add_field(name='ℹ The Following Users Are In ' + role_choice.name, value='```haskell\n' + usr + '\n```')
        await message.channel.send(None, embed=embed)
