


async def handle_data(reply, message, logger):
    if not 'status' in reply:
        logger.error('Invalid data: ' + str(reply))
        await message.channel.send('Failed')
        return

    if 'msg' in reply: 
        await message.channel.send(reply['msg'])
        return

    if reply['status'] == 0: await message.channel.send('Done')
    else:                    await message.channel.send('Failed')
