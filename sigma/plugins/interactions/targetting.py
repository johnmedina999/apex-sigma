import discord


def get_target(message, args):
    
    if message.mentions:
        return message.mentions[0]
    
    if not args:
        return None

    lookup = ' '.join(args)
    target = discord.utils.find(lambda x: x.name.lower() == lookup.lower(), message.guild.members)
    if not target:
        for mem in message.guild.members:
            if mem.nick:
                if mem.nick.lower() == lookup.lower():
                    target = mem
                    break