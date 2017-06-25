import discord
import aiohttp
import lxml.html as l


async def osu(cmd, message, args):

    if not args:
        await message.channel.send(cmd.help())
        return

    if len(args) < 2:
        await cmd.bot.send_message(message.channel, cmd.help())
        return

    user_name = args[0]
    mode = args[1]

    try:
        profile_url = 'https://osu.ppy.sh/u/' + user_name
        async with aiohttp.ClientSession() as session:
            async with session.get(profile_url) as data:
                page = await data.text()
        root = l.fromstring(page)
        username = root.cssselect('.profile-username')[0].text[:-1]
    except:
        embed = discord.Embed(color=0xDB0000, title='❗ Unable to retrieve profile.')
        await message.channel.send(None, embed=embed)
        return

    user_color = str(message.author.color)[1:]
    sig_url = 'https://lemmmy.pw/osusig/sig.php?colour=hex' + user_color + '&uname=' + user_name + '&mode=' + mode + "&pp=1"

    embed = discord.Embed(color=message.author.color)
    embed.set_image(url=sig_url)
    embed.set_author(name=username + '\'s osu! Profile', url=profile_url, icon_url='http://w.ppy.sh/c/c9/Logo.png')

    await message.channel.send(None, embed=embed)
