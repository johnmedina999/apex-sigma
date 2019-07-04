import random
import aiohttp
import discord


async def xkcd(cmd, message, args):

    comic_no = str(random.randint(1, 2171))
    if args:
        if not is_int(args[0]):
            await message.channel.send(None, embed=discord.Embed(title=':exclamation: Invalid number', color=0x993333))
            return
        
        comic_no = args[0]
        
    joke_url = 'http://xkcd.com/' + comic_no + '/info.0.json'
    async with aiohttp.ClientSession() as session:
        async with session.get(joke_url) as data:
            try: joke_json = await data.json()
            except Exception:
                await message.channel.send(None, embed=discord.Embed(title=':exclamation: Requested xkcd doesn\'t exist', color=0x993333))
                return

    embed = discord.Embed(color=0x1abc9c, title='🚽 xkcd Comic #{}: {}'.format(comic_no, joke_json['title']) ).set_image(url=joke_json['img'])
    embed.set_footer(text=joke_json['alt'])

    await message.channel.send(None, embed=embed)

def is_int(s):
    try: int(s); return True
    except ValueError: return False