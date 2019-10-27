import discord
import aiohttp

from sigma.core.ctrl_client import CtrlClient
from .forum_bot_handler import handle_data


async def forum_bot(cmd, message, args):

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    try:    bot, name = args[0].split('.')
    except: bot, name = 'Core', 'help'

    data = {
        'bot'  : bot,
        'cmd'  : name,
        'args' : [],
        'key'  : message.author.id
    }

    if len(args) > 1:
        data['args'] = args[1:]

    success = await CtrlClient(cmd.log, 44444, handle_data).request(data, (message, cmd.log))
    if not success:
        await message.channel.send('Failed')