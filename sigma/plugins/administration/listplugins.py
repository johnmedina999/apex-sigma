from config import permitted_id
from ...core.plugman import PluginManager

import asyncio
import discord
import sys

async def listplugins(cmd, message, args):
    if not message.author.id in permitted_id:
        status = discord.Embed(type='rich', color=0xDB0000, title=':no_entry: Insufficient Permissions. Bot Owner or Server Admin Only.')
        await cmd.bot.send_message(message.channel, None, embed=status)
        return
        
    exists = " ".join(args) in sys.modules 
    list = cmd.bot.plugin_manager.get_plugins()
       
    embed = discord.Embed(color=0x66cc66, title='Plugins:')
    embed.add_field(name='_____________', value=list)
    await cmd.bot.send_message(message.channel, None, embed=embed)
