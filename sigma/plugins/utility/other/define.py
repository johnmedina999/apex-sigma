import discord
import aiohttp
from bs4 import BeautifulSoup

async def define(cmd, message, args):

    definition = ""
    defNum = 1
    hasPrinted = False
    defURL = r"https://www.merriam-webster.com/dictionary/"

    if not args:
        await message.channel.send(cmd.help())
        return

    try: 
        defNum = int(args[-1])
        defURL += "%20".join(args[0:-1])
    except:
        defURL += "%20".join(args)

    async with aiohttp.ClientSession() as session:
        async with session.get(defURL) as resp:
            rawDef = await resp.text()
    
    try:
        rawDef = rawDef[rawDef.index("<!--JC: actual definitions-->")-10:]
    except:
        embed = discord.Embed(title=":exclamation: The information you entered does not correlate to a Dictionary Entry.", color=0xFF0000)
        await message.channel.send(None, embed=embed)
        return

    rawDefArr = rawDef.split("<!--JC: actual definitions-->")
    soupObj = BeautifulSoup(rawDefArr[defNum], "html.parser")

    try:    
        if '<span class="intro-colon">' not in str(soupObj):
            raise Exception('The website has changed, please fix. ("intro-colon")')

        for tag in soupObj.find_all(class_="intro-colon"):
            definition += tag.text
            if(len(tag.next_sibling.strip()) == 0):
                if 'class="sx-link sc"' not in str(soupObj):
                    raise Exception('The website has changed, please fix. ("sx-link sc")')

                if hasPrinted:
                    continue
                for tag2  in soupObj.find_all(class_="sx-link sc"):
                    definition += tag2.text
                    definition += " : "
                hasPrinted = True
            else:
                definition += tag.next_sibling
                definition += " "
    except Exception as e:
        cmd.log(e)
        return

    definition.strip()
    definition = definition.replace(":"," \n— ").replace("\n", "", 1)

    if "The word you've entered" in definition:
        embed = discord.Embed(title=":smile: That definition doesn't exist, silly!", color=0xFF8EE6)
        await message.channel.send(None, embed=embed)
        return

    if "Sorry, the word you’re looking for" in definition:
        embed = discord.Embed(title=":smile: That definition doesn't exist, silly!", color=0xFF8EE6)
        await message.channel.send(None, embed=embed)
        return

    if not definition:
        embed = discord.Embed(title=":exclamation: The information you entered does not correlate to a Dictionary Entry.", color=0xFF0000)
        await message.channel.send(None, embed=embed)
    else:
        await message.channel.send("\n:books: Definition:\n" + "```"+definition+"```")
    