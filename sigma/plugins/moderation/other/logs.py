import discord
from sigma.core.logger import get_logs
from sigma.core.utils import is_num
from sigma.core.permission import check_admin
from config import permitted_id

async def logs(cmd, message, args):

    bot_owner = message.author.id in permitted_id
    if not check_admin(message.author, message.channel) and not bot_owner:
        response = discord.Embed(title='⛔ Unpermitted. Server Admin or Bot Owner Only.', color=0xDB0000)
        await message.channel.send(embed=response)
        return

    if len(args) > 0:
        if is_num(args[0]): number = int(args[0])
        else: number = 10
    else: number = 10

    if len(args) > 1: 
        if is_num(args[0]): offset = int(args[1])
        else:               offset = 0
    else:             offset = 0
   
    logs = get_logs(number+1, offset+1, f' | SRV: {message.guild.name} [{message.guild.id}]')
    
    if len(logs) == 0: await message.channel.send("Nothing found for this server")
    else: 
        msg = '\n'.join(logs) 
        msg = msg.replace(f' | SRV: {message.guild.name} [{message.guild.id}]', ' ')
        msg = msg.replace('INFO     ', '').replace('Sigma             ', ' ')

    split_msg = []
    beg = 0
    end = 1900
    
    while True:
        idx_newln = msg.rfind('\n', beg, end)
        split_msg.append(msg[beg:idx_newln])

        beg = idx_newln

        if(end + 1 > len(msg)): break
        end = min(len(msg), beg + 1900)

    for msg in split_msg:
        await message.channel.send(msg)