import random
import aiohttp
import discord

async def xkcd(cmd, message, args):

    if args:
        try: int(args[0]) # args[0] is always a string
        except ValueError:
            await message.channel.send(None, embed=discord.Embed(title=':exclamation: Invalid number', color=0x993333))
            return

        comic_no = args[0]

    # True if args is empty, False otherwise
    random_comic = (len(args) == 0)

    if not random_comic: joke_url = 'http://xkcd.com/' + comic_no + '/info.0.json'
    else:
        # To grab info of latest comic
        async with aiohttp.ClientSession() as session:
            async with session.get('http://xkcd.com/info.0.json') as data:
                joke_json = await data.json()

        joke_url = 'http://xkcd.com/' + str(random.randint(1, joke_json['num'])) + '/info.0.json'

    # To grab info of comic to be displayed
    async with aiohttp.ClientSession() as session:
        async with session.get(joke_url) as data:
            try: joke_json = await data.json()
            except:
                await message.channel.send(None, embed=discord.Embed(title=':exclamation: Requested xkcd doesn\'t exist', color=0x993333))
                return

    embed = discord.Embed(color=0x1abc9c, title='🚽 xkcd Comic #{}: {}'.format(joke_json['num'], joke_json['title']) ).set_image(url=joke_json['img'])
    embed.set_footer(text=joke_json['alt'])

    await message.channel.send(None, embed=embed)
