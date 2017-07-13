import discord
import asyncio
from sigma.core.utils import user_avatar
from .init_clock import init_clock


def get_deaf_members_count(voice_channel):
    member_count = 0
    for member in voice_channel.members:
        if not member.bot and member.voice.deaf:
            member_count += 1
    return member_count

def get_voice_members_count(voice_channel):
    member_count = 0
    for member in voice_channel.members:
        if not member.bot:
             member_count += 1
    return member_count


def music_is_ongoing(cmd, sid, voice_instance):
    queue_exists = cmd.music.get_queue(sid)
    queue_empty = cmd.music.get_queue(sid).empty()
    
    if voice_instance:
        voice_member_count = get_voice_members_count(voice_instance.channel)
    else:
        voice_member_count = 0
   
    if queue_exists and queue_empty is not True and voice_member_count != 0:
        ongoing = True
    else:
        ongoing = False

    return ongoing


async def play(cmd, message, args):
    
    if args:
        task = cmd.bot.plugin_manager.commands['queue'].call(message, args)
        cmd.bot.loop.create_task(task)
        await asyncio.sleep(3)
    
    if message.guild.id in cmd.music.initializing:
        cmd.log.warning('Play Command Ignored Due To Server Being In The Music Initialization List')
        return

    bot_voice = message.guild.voice_client
        
    if not message.author.voice:
        embed = discord.Embed(title='⚠ I don\'t see you in a voice channel', color=0xFF9900)
        await message.channel.send(None, embed=embed)
        return
        
    srv_queue = cmd.music.get_queue(message.guild.id)
    if srv_queue.empty():
        embed = discord.Embed(title='⚠ The queue is empty', color=0xFF9900)
        await message.channel.send(None, embed=embed)
        return

    if bot_voice and bot_voice.is_playing():
        embed = discord.Embed(title=f'⚠ Already playing in {message.guild.get_member(cmd.bot.user.id).voice.channel.name}', color=0xFF9900)
        await message.channel.send(None, embed=embed)
        return

    cmd.music.add_init(message.guild.id)
    cmd.bot.loop.create_task(init_clock(cmd.music, message.guild.id))

    if not bot_voice:
        try:
            try:
                can_connect = message.guild.me.permissions_in(message.author.voice.channel).connect
                can_talk = message.guild.me.permissions_in(message.author.voice.channel).speak
                    
                if not can_connect or not can_talk:
                    embed = discord.Embed(title='⚠ I am not allowed to connect and speak there.', color=0xFF9900)
                    await message.channel.send(None, embed=embed)
                    return
                
                bot_voice = await message.author.voice.channel.connect()

            except discord.ClientException:
                bot_voice = None
                for voice_instance in cmd.bot.voice_clients:
                    if voice_instance.guild.id == message.guild.id:
                        bot_voice = voice_instance

        except SyntaxError as e:
            cmd.log.error(f'ERROR: {e} | TRACE: {e.with_traceback}')

            embed = discord.Embed(color=0xDB0000)
            embed.add_field(name='❗ I was unable to connect.', value='The most common cause is your server being too far or a poor connection.')
            await message.channel.send(None, embed=embed)
            return
            
        embed = discord.Embed(title='✅ Joined ' + message.author.voice.channel.name, color=0x66cc66)
        await message.channel.send(None, embed=embed)

    voice_member_count = get_voice_members_count(message.guild.me.voice.channel)
    deaf_member_count = get_deaf_members_count(message.guild.me.voice.channel)

    if voice_member_count == deaf_member_count and deaf_member_count != 0:
        embed = discord.Embed(title=f'⚠ Warning: All of you are deaf!', color=0xFF9900)
        await message.channel.send(None, embed=embed)

    while music_is_ongoing(cmd, message.guild.id, message.guild.me.voice):
        item = await cmd.music.get_from_queue(message.guild.id)
        if message.guild.id in cmd.music.repeaters:
            await cmd.music.add_to_queue(message.guild.id, item)

        cmd.music.currents.update({message.guild.id: item})
        sound = item['sound']
        await cmd.music.make_player(bot_voice, item)
            
        cmd.db.add_stats('MusicCount')
        embed = discord.Embed(color=0x0099FF)
        
        if item['type'] == 0:
            embed.add_field(name='🎵 Now Playing', value=sound.title)
            embed.set_thumbnail(url=sound.thumb)
            embed.set_author(name=f'{item["requester"].name}#{item["requester"].discriminator}', icon_url=user_avatar(item['requester']), url=item['url'])
            embed.set_footer(text=f'Duration: {sound.duration}')
        elif item['type'] == 1:
            embed.add_field(name='🎵 Now Playing', value=sound['title'])
            embed.set_thumbnail(url=sound['artwork_url'])
            embed.set_author(name=f'{item["requester"].name}#{item["requester"].discriminator}', icon_url=user_avatar(item['requester']), url=item['url'])
        else:
            return
            
        await message.channel.send(None, embed=embed)
        while bot_voice.is_playing():
            await asyncio.sleep(2)

    try: await bot_voice.disconnect()
    except: pass

    del cmd.music.currents[message.guild.id]