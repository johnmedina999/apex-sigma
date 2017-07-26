import discord


async def skip(cmd, message, args):
    
    if not message.author.voice:
        embed = discord.Embed(color=0xFF9900, title='⚠ You are not in a voice channel')
        await message.channel.send(None, embed=embed)
        return

    queue = cmd.bot.music.get_queue(message.guild.id)
    if not queue or queue.empty():
        embed = discord.Embed(color=0xFF9900, title='⚠ The Queue Is Empty or This Is The Last Song')
        await message.channel.send(None, embed=embed)
        return

    if message.guild.voice_client:
        voice = message.guild.voice_client
        voice.stop()