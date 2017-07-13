import discord


async def pause(cmd, message, args):
    
    player = message.guild.voice_client
    
    if not player:
        response = discord.Embed(color=0xFF9900, title='⚠ No Player Exists.')
        await message.channel.send(None, embed=response)    
        return

    if not player.is_playing():
        response = discord.Embed(color=0xFF9900, title='⚠ Already Paused.')
        await message.channel.send(None, embed=response)
        return    
    
    player.pause()
    
    response = discord.Embed(color=0x0099FF, title='⏸ Player Paused')
    await message.channel.send(None, embed=response)
