import random
import aiohttp
import discord


async def xkcd(cmd, message, args):

    comic_no = str(random.randint(1, 1724))
    if args:
        if is_int(args[0]):
            comic_no = args[0]
        else:
            embed = discord.Embed(title=':exclamation: Invalid number', color=0x993333)
            await cmd.bot.send_message(message.channel, None, embed=embed)
            return

    joke_url = 'http://xkcd.com/' + comic_no + '/info.0.json'

    async with aiohttp.ClientSession() as session:
        async with session.get(joke_url) as data:
            try:
                joke_json = await data.json()
            except Exception:
                embed = discord.Embed(title=':exclamation: Requested XKCD doesn\'t exist', color=0x993333)
                await cmd.bot.send_message(message.channel, None, embed=embed)
                return


    image_url = joke_json['img']
    embed = discord.Embed(color=0x1abc9c, title='🚽 An XKCD Comic')
    embed.set_image(url=image_url)

    await cmd.bot.send_message(message.channel, None, embed=embed)

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False