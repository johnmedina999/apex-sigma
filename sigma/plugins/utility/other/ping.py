import discord


async def ping(cmd, message, args):
    embed = discord.Embed(title='Pong!', color=0x0099FF)
    await message.channel.send(None, embed=embed)
