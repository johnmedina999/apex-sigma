import math
import asyncio
import discord


async def master_color(ev):

    tick = 0.0
    while True:
        
        tick = tick + 1.0
        freq = (math.pi * 2.0) / 86400.0 * 10.0

        red = int((math.sin(freq*30.0*tick + 2.0) * 127.0 + 128.0))
        green = int((math.sin(freq*23.0*tick + 0.0) * 127.0 + 128.0))
        blue = int((math.sin(freq*7.0*tick + 4.0) * 127.0 + 128.0))

        for guild in ev.bot.guilds:
            try:
                master_color_role = [role for role in guild.roles if role.name == "master_color"][0]
                await master_color_role.edit(colour=discord.Colour.from_rgb(red, green, blue))
            except: pass

        await asyncio.sleep(60)