import discord
from sigma.core.permission import check_admin


async def greet(cmd, message, args):
    
    if not check_admin(message.author, message.channel):
        embed = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
        await message.channel.send(None, embed=embed)
        return

    active = cmd.db.get_settings(message.guild.id, 'Greet')
    greet_channel = cmd.db.get_settings(message.guild.id, 'GreetChannel')
    
    if not active:
        if not greet_channel:
            cmd.db.set_settings(message.guild.id, 'GreetChannel', message.guild.default_channel.id)
    
        cmd.db.set_settings(message.guild.id, 'Greet', True)
        embed = discord.Embed(color=0x66CC66,title='✅ Greeting Messages Enabled')
    else:
        cmd.db.set_settings(message.guild.id, 'Greet', False)
        embed = discord.Embed(color=0x66CC66, title='✅ Greeting Messages Disabled')
    
    await message.channel.send(None, embed=embed)
