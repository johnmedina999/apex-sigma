import discord
from sigma.core.permission import check_man_roles
from sigma.core.rolecheck import matching_role

async def setcolor(cmd, message, args):
    # if no args, send help message
    if not args:
        await message.channel.send(cmd.help())
        return

    # checks permissions
    if not check_man_roles(message.author, message.channel):
        out_content = discord.Embed(type='rich', color=0xDB0000, title='⛔ Error')
        out_content.add_field(name='Insufficient Permissions', value='You require the Manage Roles permission.')
        await message.channel.send(None, embed=out_content)
        return

    color = args[0].lstrip('#').upper()
    # check if color is a proper format
    if not is_valid_hex(color):
        out_content = discord.Embed(type='rich', color=0xFF9900, title='⚠ Error')
        out_content.add_field(name='Invalid Input', value='A valid hexadecimal color code has numbers from 0–9 and letters from A–F, and has six characters.')
        await message.channel.send(None, embed=out_content)
        return

    # check if user has role
    target = message.author if not message.mentions else message.mentions[0]
    has_role = discord.utils.get(target.roles, name=color) #returns None if no role found
    if has_role:
        out_content = discord.Embed(type='rich', color=0xFF9900, title='⚠ Error')
        out_content.add_field(name='Role Present', value=f'This user already has the role **{color}**.')
        await message.channel.send(None, embed=out_content)
        return

    # check if role exists
    exists = matching_role(message.guild, color)
    if not exists:
        discord_colour = discord.Colour(int(color, 16))
        target_role = await message.guild.create_role(name=color, colour=discord_colour, reason="Color role")
    else:
        target_role = exists

    # loop through list of user's roles and delete/remove any color roles as necessary
    for role in target.roles:
        if is_valid_hex(role.name):
            if len(role.members) == 1:
                await role.delete()
            else:
                await target.remove_roles(role)

    await target.add_roles(target_role)

    # display confirmation
    out_content = discord.Embed(type='rich', color=int(color, base=16), title='✅ Success')
    out_content.add_field(name='Role Added Successfully', value=f'Role **{target_role.name}** was added to <@{target.id}>.')
    await message.channel.send(None, embed=out_content)

def is_valid_hex(x):
    """Checks to see if param x is a valid hexadecimal color code (alphanumeric 0–9, A-F; six characters).

    Returns a boolean."""
    try:
        int(x, 16) #if it's not hexadecimal, it will raise ValueError
        if len(x) != 6:
            raise ValueError
        return True
    except ValueError:
        return False
