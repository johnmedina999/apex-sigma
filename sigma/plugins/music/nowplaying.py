﻿import discord
from sigma.core.utils import user_avatar

async def nowplaying(cmd, message, args):
    
    if message.guild.id not in cmd.music.currents:
        embed = discord.Embed(color=0x0099FF, title='ℹ No Currently Playing Item')
        await message.channel.send(None, embed=embed)
        return

    item = cmd.music.currents[message.guild.id]
    sound = item['sound']
        
    embed = discord.Embed(color=0x0099FF)
    embed.set_footer(text='You can click the author to go to the song\'s page.')
    
    if item['type'] == 0:
        embed.add_field(name='🎵 Now Playing', value=sound.title)
        embed.set_thumbnail(url=sound.thumb)
        embed.set_author(name=f'{item["requester"].name}#{item["requester"].discriminator}', icon_url=user_avatar(item['requester']), url=item['url'])
        embed.set_footer(text=f'Duration: {sound.duration}')
    elif item['type'] == 1:
        embed.add_field(name='🎵 Now Playing', value=sound['title'])
        embed.set_thumbnail(url=sound['artwork_url'])
        embed.set_author(name=f'{item["requester"].name}#{item["requester"].discriminator}', icon_url=user_avatar(item['requester']), url=item['url'])
        
    await message.channel.send(None, embed=embed)
    
