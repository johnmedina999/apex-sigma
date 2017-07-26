from sigma.core.permission import check_admin


async def sfiexec(ev, message, args):

    if 'discord.gg' not in message.content: return
    if check_admin(message.author, message.channel): return

    active = ev.db.get_settings(message.guild.id, 'BlockInvites')
    if not active: return
    
    try: await message.delete()
    except Exception as e: ev.log.error(e)
