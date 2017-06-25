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

    else:
        success = cmd.bot.plugin_manager.reload_plugin("".join(args))

        if not success:
            out_content = discord.Embed(type='rich', color=0x660000, title=':exclamation: Plugin failed to reload')
        else:
            out_content = discord.Embed(type='rich', color=0x66cc66, title=':white_check_mark: Plugin reloaded')

        await message.channel.send(None, embed=out_content)
