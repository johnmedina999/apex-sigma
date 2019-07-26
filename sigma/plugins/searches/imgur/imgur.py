import random
import imgurpython
import discord
from config import ImgurClientID, ImgurClientSecret


async def imgur(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help())
        return

    if (ImgurClientID == '') or (ImgurClientSecret == ''):
        embed = discord.Embed(color=0xDB0000)
        embed.add_field(name='API key ImgurClientID and/or ImgurClientSecret not found.', value='Please ask the bot owner to add them.')
        await message.channel.send(None, embed=embed)
        return

    q = ' '.join(args)
    imgur_client = imgurpython.ImgurClient(ImgurClientID, ImgurClientSecret)
    gallery_items = imgur_client.gallery_search(q, advanced=None, sort='time', window='all', page=0)
    
    chosen_item = random.choice(gallery_items).link
    await message.channel.send(chosen_item)
