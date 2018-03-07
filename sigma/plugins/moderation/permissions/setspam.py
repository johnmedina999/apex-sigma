from sigma.core.permission import check_admin
from sigma.core.permission import check_write
from config import Prefix
import discord


async def setspam(cmd, message, args):
    
    if not check_admin(message.author, message.channel):
        # user is no server admin
        embed = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
        await message.channel.send(None, embed=embed)
        return

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    try: 
        spam_threshold = int(args[0])
        cmd.db.set_settings(message.guild.id, 'SpamThreshold', spam_threshold)
    except: 
        await message.channel.send(cmd.help())
        return
    
    embed = discord.Embed(title='✅ Spam monitor settings updated', color=0x66CC66)
    await message.channel.send(None, embed=embed)
