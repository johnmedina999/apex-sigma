import sys

from config import permitted_id


async def kill(cmd, message, args):
    if message.author.id in permitted_id:
        await cmd.reply('I\'ll be back...')

        cmd.log.info('Terminated by user {:s}'.format(message.author.name))
        sys.exit('terminated by command')
