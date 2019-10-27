import discord


async def handle_data(reply, message, logger):
    if reply == None:
        logger.error('Cmd reply is none')
        await message.channel.send('Something went horribly wrong!')
        return

    if not 'status' in reply:
        logger.error('Invalid data: ' + str(reply))
        await message.channel.send('Failed')
        return
    
    if 'msg' in reply: msg = str(reply['msg'])
    else:              msg = 'Done' if reply['status'] == 0 else 'Failed'

    if reply['status'] == -1:  embed = discord.Embed(color=0x880000, description=msg)
    elif reply['status'] == 0: embed = discord.Embed(color=0x008800, description=msg)
    else:                      embed = discord.Embed(color=0x880088, description=msg)

    await message.channel.send(None, embed=embed)
