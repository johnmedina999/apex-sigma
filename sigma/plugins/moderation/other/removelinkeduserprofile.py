import discord
from sigma.core.permission import check_man_srv, check_man_roles
from config import permitted_id


async def removelinkeduserprofile(cmd, message, args):
    
    if not message.mentions:
        out_content = discord.Embed(type='rich', color=0xDB0000, title='❗ Error')
        out_content.add_field(name='Invalid Arguments', value=cmd.help())
        await message.channel.send(None, embed=out_content)
        return

    target = message.mentions[0]
    if len(args) > 1: account_type = args[1]
    else:             account_type = None

    if account_type is None:
        if not message.author.id in permitted_id:
            embed = discord.Embed(type='rich', color=0xDB0000, title='⛔ Only Bot Owner can remove the entire user entry. Please specify the specific linked profile to remove instead.')
            await message.channel.send(None, embed=embed)
            return

    if account_type is not None:
        if (message.author.id != target.id) and not check_man_roles(message.author, message.channel):
            embed = discord.Embed(type='rich', color=0xDB0000, title='⛔ Insufficient Permissions. Requires Manage Roles Permission For Modifying Others Users\' Linked Profiles.')
            await message.channel.send(None, embed=embed)
            return

    cmd.db.removeDiscordProfileLink(target.id, account_type)
    
    embed = discord.Embed(type='rich', color=0x66CC66, title='✅ ' + 'Removed profile link(s) for ' + target.name)
    await message.channel.send(None, embed=embed)

    
