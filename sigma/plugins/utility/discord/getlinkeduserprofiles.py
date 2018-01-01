import discord


async def getlinkeduserprofiles(cmd, message, args):
    args = [arg for arg in args if arg.strip() != '']

    if not message.mentions:
        out_content = discord.Embed(type='rich', color=0xDB0000, title='❗ Error')
        out_content.add_field(name='Invalid Arguments', value=cmd.help())
        await message.channel.send(None, embed=out_content)
        return

    target = message.mentions[0]
    if len(args) > 1: account_type = args[1]
    else:             account_type = None
    
    profile_links = cmd.db.getDiscordProfileLink(target.id, account_type)
    if not profile_links:
        out_content = discord.Embed(type='rich', color=0xDB0000, title='❗ No profiles linked for ' + target.name)
        await message.channel.send(None, embed=out_content)
        return

    profile_types = profile_links.keys()
    profile_types = [ profile_type[:8] + '...' if len(profile_type) > 8 else profile_type for profile_type in profile_types ]

    links = profile_links.values()
    links = [ '[' + link[:32] + '...](' + link + ')' if len(link) > 32 else link for link in links ]

    embed = discord.Embed(type='rich', color=0x66CC66)
    embed.set_author(name=target.name, icon_url=target.avatar_url)
    embed.add_field(name='Profile', value='\n'.join(profile_types), inline=True)
    embed.add_field(name='Profile link', value='\n'.join(links), inline=True)
    
    await message.channel.send(None, embed=embed)