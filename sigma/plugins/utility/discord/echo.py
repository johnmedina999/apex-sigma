from sigma.core.permission import check_mention_everyone


async def echo(cmd, message, args):
    msg = ' '.join(args)

    if not check_mention_everyone(message.author, message.channel):
        msg = msg.replace('@everyone', 'everyone')

    await message.channel.send(msg)
