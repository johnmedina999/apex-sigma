import math
import asyncio
import discord

from sigma.core.permission import check_admin
from config import permitted_id

def color_func_sin(x, period):
    return int((255.0*math.sin(((2.0*math.pi)/86400.0)*period*x)+255.0)/2.0)

def color_func_cos(x, period):
    return int((255.0*math.cos(((2.0*math.pi)/86400.0)*period*x)+255.0)/2.0)

async def master_color(ev):
    
    bot_owner = discord.utils.find(lambda x: x.id == permitted_id[0], ev.bot.get_all_members())
    if not bot_owner: 
        print("[WARNING] master_color.py: bot owner not found in any servers")
        return

    servers = ev.bot.guilds
    red = 0; green = 0; blue = 0

    while True:
        
        red = red + 1
        green = green + 1
        blue = blue + 1

        red_out = color_func_sin(red, 24)
        green_out = color_func_cos(red, 20)
        blue_out = color_func_sin(red, 25)

        for server in servers:
            if server.owner != bot_owner: continue
            if len(server.owner.top_role.members) > 1: continue

            await server.owner.top_role.edit(colour=discord.Colour.from_rgb(red_out, green_out, blue_out))

        await asyncio.sleep(1)