import discord
import imgurpython

from config import ImgurClientID, ImgurClientSecret
imgur_client = None

async def imgurlink(cmd, message, args):

    if not args:
        await message.channel.send(cmd.help())
        return

    if (ImgurClientID == '') or (ImgurClientSecret == ''):
        embed = discord.Embed(color=0xDB0000)
        embed.add_field(name='API key ImgurClientID and/or ImgurClientSecret not found.', value='Please ask the bot owner to add them.')
        await message.channel.send(None, embed=embed)
        return

    try:
        imgur_client = imgurpython.ImgurClient(ImgurClientID, ImgurClientSecret)
    except Exception as e:
        cmd.log.error(e)
        await message.channel.send('Something went wrong! Contact the bot dev.')
        return

    if message.attachments or args:
        if message.attachments:
            img_url = message.attachments[0].url
        else:
            img_url = ' '.join(args)
        if img_url.startswith('http'):
            upload_res = imgur_client.upload_from_url(img_url)
            response = discord.Embed(color=0x66CC66)
            response.add_field(name='✅ Image Uploaded', value=f'URL:\n```\n{upload_res["link"]}\n```')
            response.set_image(url=upload_res['link'])
        else:
            response = discord.Embed(color=0xDB0000, title='❗ Invalid URL')
    else:
        response = discord.Embed(color=0xDB0000, title='❗ Nothing Was Inputted')
    await message.channel.send(embed=response)
