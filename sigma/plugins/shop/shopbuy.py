﻿import discord
from sigma.core.rolecheck import matching_role, user_matching_role


async def shopbuy(cmd, message, args):
    
    if not args:
        status = discord.Embed(type='rich', color=0xDB0000, title='❗ Insufficient Arguments.')
        await message.channel.send(None, embed=status)
        return
    
    role_name = ' '.join(args)
    item_list = cmd.db.get_settings(str(message.guild.id), 'ShopItems')
    
    for item in item_list:
        if item['RoleName'].lower() != role_name.lower(): continue

        found = True
        price = abs(int(item['Price']))
        role = matching_role(message.guild, role_name)
        
        if user_matching_role(message.author, role_name):
            status = discord.Embed(type='rich', color=0xFF9900, title='⚠ You already have this role.')
            await message.channel.send(None, embed=status)
            return

        user_points = cmd.db.get_points(message.author)

        if user_points['Current'] < price:
            status = discord.Embed(type='rich', color=0xFF9900, title='⚠ You can\'t afford it.')
            await message.channel.send(None, embed=status)
            return
            
        await message.author.add_roles(role)
        cmd.db.take_points(message.guild, message.author, price)
        
        status = discord.Embed(type='rich', color=0x66cc66, title='✅ You bought ' + role.name + ' .')
        await message.channel.send(None, embed=status)            
        return
    
    status = discord.Embed(type='rich', color=0xDB0000, title='❗ Couldn\'t find  this in the shop.')
    await message.channel.send(None, embed=status)
