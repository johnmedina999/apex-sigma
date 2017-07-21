from config import permitted_id
from ...core.plugman import PluginManager

import asyncio
import discord
import sys


async def reloadplugin(cmd, message, args):
    
    if not message.author.id in permitted_id:
        status = discord.Embed(type='rich', color=0xDB0000, title=':no_entry: Insufficient Permissions. Bot Owner or Server Admin Only.')
        await message.channel.send(None, embed=status)
        return

    if not args:
        out_content = discord.Embed(type='rich', color=0xDB0000, title=':exclamation: No plugin specified')
        await message.channel.send(None, embed=out_content)
        return

    try: cmd.bot.plugin_manager.reload_plugin(" ".join(args))
    except Exception as e:
        if str(e).find("[Warning]") != -1:
            out_content = discord.Embed(type='rich', color=0x666600, title=':warning: Plugin reloaded')
            out_content.add_field(name='\_\_\_\_\_\_\_\_\_\_\__', value=e)
        else:
            out_content = discord.Embed(type='rich', color=0x660000, title=':exclamation: Plugin failed to reload')
            out_content.add_field(name='\_\_\_\_\_\_\_\_\_\_\__', value=e)

        await message.channel.send(None, embed=out_content)
        return

    out_content = discord.Embed(type='rich', color=0x66cc66, title=':white_check_mark: Plugin reloaded')
    await message.channel.send(None, embed=out_content)
