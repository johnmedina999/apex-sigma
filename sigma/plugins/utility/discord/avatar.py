import discord
from PIL import Image
from io import BytesIO
import aiohttp
import os

async def avatar(cmd, message, args):
    if message.mentions:
        target = message.mentions[0]
    else:
        target = message.author
    
    async with aiohttp.ClientSession() as session:
        async with session.get(target.avatar_url) as data:
           avatar_img_raw = await data.read()

    try: avatar_img = Image.open(BytesIO(avatar_img_raw))
    except: cmd.log.error("Could not open raw image"); raise

    if target.avatar_url.find(".webp") != -1:
        avatar_img = avatar_img.convert("RGB") 

    output_location = 'cache/avatar' + str(message.author.id) + '.png'
    avatar_img.save(output_location)

    with open(output_location, 'rb') as img:
        await message.channel.send(file=discord.File(img))
    os.remove(output_location)