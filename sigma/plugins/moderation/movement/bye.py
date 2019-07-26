import discord
from sigma.core.permission import check_admin


async def bye(cmd, message, args):
    
    if not check_admin(message.author, message.channel):
        embed = discord.Embed(title='⛔ Unpermitted. Server Admin Only.', color=0xDB0000)
        await message.channel.send(None, embed=embed)
        return

    active = cmd.db.get_settings(message.guild.id, 'Bye')
    greet_channel = cmd.db.get_settings(message.guild.id, 'ByeChannel')

    if not active:
        if not greet_channel: return

        cmd.db.set_settings(message.guild.id, 'Bye', True)
        embed = discord.Embed(color=0x66CC66, title='✅ Goodbye Messages Enabled')
    else:
        cmd.db.set_settings(message.guild.id, 'Bye', False)
        embed = discord.Embed(color=0x66CC66, title='✅ Goodbye Messages Disabled')

    await message.channel.send(None, embed=embed)
