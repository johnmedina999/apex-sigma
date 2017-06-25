import discord


async def ping(cmd, message, args):
    embed = discord.Embed(title='Pong!', color=0x0099FF)
    await cmd.bot.send_message(message.channel, None, embed=embed)
