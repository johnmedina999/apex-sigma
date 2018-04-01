from sigma.core.permission import check_admin
from sigma.core.permission import check_write
from config import Prefix
import discord


async def moderatorchannel(cmd, message, args):
    
    if not check_admin(message.author, message.channel):
        # user is no server admin
        embed = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
        await message.channel.send(None, embed=embed)
        return

    if message.channel_mentions:
        # argument exists and is a channel
        # channel can be written to -> turn on moderator notifications and set channelid
        cmd.db.set_settings(message.guild.id, 'ModeratorNotifications', True)
        cmd.db.set_settings(message.guild.id, 'ModeratorChannel', message.channel_mentions[0].id)
        embed = discord.Embed(title='✅ Moderator notifications will be posted to #' +  message.channel_mentions[0].name, color=0x66CC66)
    elif len(args) == 0:
        # no argument given, moderator notifications will be turned off
        cmd.db.set_settings(message.guild.id, 'ModeratorNotifications', False)
        embed = discord.Embed(title='✅ Moderator notifications turned OFF for this server', color=0x66CC66)
        embed.add_field(name='Note:', value='Use "' + Prefix + 'moderatorchannel #channel_name" to turn them back on.')
    else:
        # given argument is not a channel
        embed = discord.Embed(title=':x: "' + args[0] + '" is not a channel', color=0xDB0000)
        embed.add_field(name='Note:', value='Enter a channel in this format: "#channel_name" or leave blank to turn announcements off.')
    
    await message.channel.send(None, embed=embed)
