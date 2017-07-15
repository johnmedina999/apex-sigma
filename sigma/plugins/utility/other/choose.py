import random
import discord


async def choose(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help())
        return
    
    choice = random.choice(args)
    embed = discord.Embed(color=0x1ABC9C, title=':thinking: I choose... ' + choice)
    await message.channel.send(None, embed=embed)