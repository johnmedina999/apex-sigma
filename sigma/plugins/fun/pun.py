import aiohttp
import discord


async def pun(cmd, message, args):
    cmd.db.add_stats('CancerCount')
    pun_url = 'http://www.punoftheday.com/cgi-bin/arandompun.pl'

    async with aiohttp.ClientSession() as session:
        async with session.get(pun_url) as data:
            pun_req = await data.text()

    pun_text = str(pun_req)
    pun_text = pun_text[pun_text.find('&quot;') + len('&quot;') : len(pun_text)]  # strip left side
    pun_text = pun_text[0 : pun_text.find('&quot;')]                              # strip right side
    pun_text = pun_text.replace('&rsquo;', '\'')                                  # Factor in apostrophe encoding

    embed = discord.Embed(color=0x1abc9c)
    embed.add_field(name='😒 Have A Pun', value='```\n' + pun_text + '\n```')
    await cmd.bot.send_message(message.channel, None, embed=embed)
