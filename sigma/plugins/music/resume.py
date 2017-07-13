import discord


async def resume(cmd, message, args):
    
    player = message.guild.voice_client
    
    if not player:
        response = discord.Embed(color=0xFF9900, title='⚠ No Player Exists.')
        await message.channel.send(None, embed=response)
        return

    if player.is_playing():
        response = discord.Embed(color=0xFF9900, title='⚠ Already Playing.')
        await message.channel.send(None, embed=response)
        return

    player.resume()
    
    response = discord.Embed(color=0x0099FF, title='▶ Player Resumed')
    await message.channel.send(None, embed=response)
