from config import permitted_id
import discord


async def leave(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help())
        return

    if not message.author.id in permitted_id:
        out = discord.Embed(type='rich', color=0xDB0000, title=':no_entry: Insufficient Permissions. Bot Owner Only.')
        await message.channel.send(None, embed=out)
        return

    search_id = int(args[0])
    try:
        for server in cmd.bot.guilds:
            if server.id != int(search_id): continue

            s_name = server.name
            await server.leave()
        
            out = discord.Embed(title=':outbox_tray: I have left ' + s_name, color=0x66CC66)
            await message.channel.send(None, embed=out)
            return
         
        out = discord.Embed(title='❗ No server with that ID found.', color=0xDB0000)
        await message.channel.send(None, embed=out)

    except Exception as e:
       cmd.log.error(e)
        
