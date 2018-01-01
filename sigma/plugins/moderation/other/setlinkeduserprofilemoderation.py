import discord
from sigma.core.permission import check_man_srv


async def setlinkeduserprofilemoderation(cmd, message, args):
    args = [arg for arg in args if arg.strip() != '']
    
    if not message.mentions:
        out_content = discord.Embed(type='rich', color=0xDB0000, title='❗ Error')
        out_content.add_field(name='Invalid Arguments', value=cmd.help())
        await message.channel.send(None, embed=out_content)
        return
    
    if len(args) < 2:
        out_content = discord.Embed(type='rich', color=0xDB0000, title='❗ Error')
        out_content.add_field(name='Missing Arguments', value=cmd.help())
        await message.channel.send(None, embed=out_content)
        return

    if not check_man_srv(message.author, message.channel):
        embed = discord.Embed(type='rich', color=0xDB0000, title='⛔ Insufficient Permissions. Requires Manage Server Permision')
        await message.channel.send(None, embed=embed)
        return

    target = message.mentions[0]

    if args[1] is 'enable':    moderation = True
    elif args[1] is 'disable': moderation = False
    else:
        out_content = discord.Embed(type='rich', color=0xDB0000, title='❗ Error')
        out_content.add_field(name='Invalid Arguments', value=cmd.help())
        await message.channel.send(None, embed=out_content)
        return

    cmd.db.setModerationDiscordProfileLink(target.id, moderation)

    embed = discord.Embed(type='rich', color=0x66CC66, title='✅ ' + 'Enabled' if moderation is True else 'Disabled' + ' profile link moderation for ' + target.name)
    await message.channel.send(None, embed=embed)

    
