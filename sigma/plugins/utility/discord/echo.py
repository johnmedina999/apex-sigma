import discord
from sigma.core.permission import check_mention_everyone


async def echo(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help())
        return

    embed = discord.Embed(type='rich', color=0x66CC66)
    
    if args[0] == "-anon": 
        msg = ' '.join(args[1:])
    else:
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url, url=message.author.avatar_url)
        msg = ' '.join(args)
    
    if not check_mention_everyone(message.author, message.channel):
        msg = msg.replace('@everyone', 'everyone')

    if len(msg) > 0:
        embed.add_field(name='\x00', value=msg)

    try: await message.delete()
    except: pass

    await message.channel.send(None, embed=embed)

    
