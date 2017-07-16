import math
import asyncio
import discord

from sigma.core.permission import check_admin
from config import permitted_id



async def master_color(ev):
    ev.bot.loop.create_task(colorer(ev))



async def colorer(ev):
    
    bot_owner = discord.utils.find(lambda x: x.id == permitted_id[0], ev.bot.get_all_members())
    if not bot_owner: 
        print("[WARNING] master_color.py: bot owner not found in any servers")
        return

    servers = ev.bot.guilds
    tick = 0.0

    while True:
        
        tick = tick + 1.0
        freq = (math.pi * 2.0) / 86400.0 * 10.0

        try:
            red_out = int((math.sin(freq*30.0*tick + 2.0) * 127.0 + 128.0))
            green_out = int((math.sin(freq*23.0*tick + 0.0) * 127.0 + 128.0))
            blue_out = int((math.sin(freq*7.0*tick + 4.0) * 127.0 + 128.0))

            for server in servers:
                if server.owner != bot_owner: continue
                if len(server.owner.top_role.members) > 1: continue

                await server.owner.top_role.edit(colour=discord.Colour.from_rgb(red_out, green_out, blue_out))
        except: pass

        await asyncio.sleep(1)