import discord
from sigma.core.permission import check_man_roles
from sigma.core.rolecheck import matching_role

async def addselfcolorrole(cmd, message, args):
    # if no args, send help message
    if not args:
        await message.channel.send(cmd.help())
        return

    # checks permissions
    if not check_man_roles(message.author, message.channel):
        out_content = discord.Embed(type='rich', color=0xDB0000, title='⛔ Insufficient Permissions. Server Admin Only.')
        await message.channel.send(None, embed=out_content)
        return

    # create color and name from user input
    color = args[0].lstrip('#').upper()

    # check if color is a proper format
    try:
        int(color, 16) #if it's not hexadecimal, it will raise ValueError
        if len(color) != 6:
            raise ValueError
    except ValueError:
        out_content = discord.Embed(type='rich', color=0xFF9900, title='⚠ Error')
        out_content.add_field(name='Invalid Input', value='A valid hexadecimal color code has numbers from 0–9 and letters from A–F, and has six characters.')
        await message.channel.send(None, embed=out_content)
        return

    # check if role exists
    exists = matching_role(message.guild, color)
    if exists:
        out_content = discord.Embed(type='rich', color=0xFF9900, title='⚠ Error')
        out_content.add_field(name='Role Exists', value=f'A role with the name **{color}** already exists.')
        await message.channel.send(None, embed=out_content)
        return

    # create role
    discord_colour = discord.Colour(int(color, 16))
    created_role = await message.guild.create_role(name=color, colour=discord_colour, reason="Color role")

    # retrieve self roles
    self_roles = cmd.db.get_settings(str(message.guild.id), 'SelfRoles')

    # add role to self_roles
    self_roles.append(created_role.id)
    cmd.db.set_settings(str(message.guild.id), 'SelfRoles', self_roles)

    # display confirmation
    out_content = discord.Embed(type='rich', color=int(color, base=16), title=f'✅ Role **{created_role.name}** created and added to the self assignable roles list.')
    await message.channel.send(None, embed=out_content)
