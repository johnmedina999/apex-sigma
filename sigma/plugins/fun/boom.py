import discord
import asyncio

async def boom(cmd, message, args):
    
    bomb = await message.channel.send(":bomb:")
    await asyncio.sleep(5)
    await bomb.edit(content=":boom:")