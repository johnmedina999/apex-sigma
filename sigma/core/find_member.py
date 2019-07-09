import discord

class MemberNotFoundError(discord.DiscordException):
    pass

async def find_member(user, guild=discord.Guild):
    for member in guild.members:
        if user in (member.nick, member.display_name, member.id, member.name):
            return member
    raise MemberNotFoundError(f'Member {user} not found.')
