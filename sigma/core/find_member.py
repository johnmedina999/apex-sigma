async def find_member(guild, user):
    for member in guild.members:
        if user in (member.nick, member.display_name, member.id, member.name):
            return member
