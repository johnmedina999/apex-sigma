import discord
from sigma.core.logger import get_logs
from sigma.core.utils import is_num

async def logs(cmd, message, args):

    if not args[0]: number = 10
    elif is_num(args[0]): number = int(args[0])
    else: number = 10

    if len(args) < 2: server = message.guild.id
    else: server  = args[1]

    logs = get_logs(number)

    for log in logs[:]:
        if log.find(' [' + server + '] | ') == -1:
            logs.remove(log)
    
    if len(logs) == 0: await message.channel.send("Nothing found for server specified: " + str(server))
    else: await message.channel.send(''.join(logs))