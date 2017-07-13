import discord


async def disconnect(cmd, message, args):
    
    if not message.author.voice:
        embed = discord.Embed(title='⚠ I don\'t see you in a voice channel', color=0xFF9900)
        await message.channel.send(None, embed=embed)
        return

    voice = message.guild.voice_client
    if not voice:
        embed = discord.Embed(title='⚠ I am not in a voice channel', color=0xFF9900)
        await message.channel.send(None, embed=embed)
        return
    
    cmd.music.purge_queue(message.guild.id)
    voice.stop()
    await voice.disconnect()
    
    embed = discord.Embed(color=0x66CC66, title=f'✅ Disconnected From {voice.channel.name}')
    embed.set_footer(text='And purged queue.')            
    await message.channel.send(None, embed=embed)
