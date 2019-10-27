import discord
import aiohttp

from sigma.core.ctrl_client import CtrlClient
from .forum_bot_handler import handle_data


async def forum_bot(cmd, message, args):

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    bot, name = args[0].split('.')

    data = {
        'bot'  : bot,
        'cmd'  : name,
        'args' : []
    }

    if len(args) > 1: 
        data['args'] = args[1:]


    success = await CtrlClient(cmd.log, 44444, handle_data).request(data, (message, cmd.log))
    if not success:
        await message.channel.send('Failed')