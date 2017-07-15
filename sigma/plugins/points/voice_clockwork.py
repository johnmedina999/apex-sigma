import asyncio
import random


def count_members(guild):
    counter = 0
    for member in guild.members:
        if member.bot: continue
        counter += 1
    return counter


def count_vc_members(vc):
    counter = 0
    for member in vc.members:
        if member.bot: continue
        if member.voice.deaf: continue
        if member.voice.self_deaf: continue
        counter += 1
    
    return counter


async def voice_clockwork(ev):
    while True:
        members = ev.bot.get_all_members()
        for member in members:
            if member.bot: continue
            if not member.voice: continue
            
            afk = False
            
            if not member.guild.afk_channel: continue
            
            afk_id = member.guild.afk_channel.id
            vc_id = member.voice.channel.id
            
            if vc_id == afk_id:
                afk = True
        
            if count_members(member.guild) >= 20:
                if afk: continue
                if member.voice.deaf: continue
                if member.voice.self_deaf: continue
                if count_vc_members(member.voice.channel) > 1:
                    points = random.randint(2, 10)
                    ev.db.add_points(member.guild, member, points)
        
        await asyncio.sleep(20)