import discord
from sigma.core.permission import check_man_roles, check_man_srv


async def linkuserprofiles(cmd, message, args):
    
    if len(args) < 2:
        out_content = discord.Embed(type='rich', color=0xDB0000, title='❗ Error')
        out_content.add_field(name='Missing Arguments', value=cmd.help())
        await message.channel.send(None, embed=out_content)
        return

    if message.mentions: target = message.mentions[0]
    else:                target = message.author
    
    account_type = args[1]
    account_link = args[2]

    if (message.author.id != target.id) and not check_man_roles(message.author, message.channel):
        embed = discord.Embed(type='rich', color=0xDB0000, title='⛔ Insufficient Permissions. Requires Manage Roles Permission For Modifying Others Users\' Linked Profiles.')
        await message.channel.send(None, embed=embed)
        return

    if (message.author.id == target.id) and not check_man_srv(message.author, message.channel):
        try:
            if cmd.db.isModerationDiscordProfileLink(target.id) is True:
                embed = discord.Embed(type='rich', color=0xDB0000, title='⛔ You have been restricted from modifying your own profile links.')
                await message.channel.send(None, embed=embed)
                return
        except: pass  # Profile doesn't exist yet. No moderation control (yet)

    cmd.db.updateDiscordProfileLink(target.id, account_type, account_link)

    embed = discord.Embed(type='rich', color=0x66CC66, title='✅ Linked ' + target.name + '\'s profile to ' + account_type)
    await message.channel.send(None, embed=embed)

    
