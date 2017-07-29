import discord
import aiohttp
from bs4 import BeautifulSoup

async def listsubforum(cmd, message, args):

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    forum_id = args[0]

    # Get the HTML page
    subforum_url = 'https://osu.ppy.sh/community/forums/' + forum_id
    async with aiohttp.ClientSession() as session:
        async with session.get(subforum_url) as data:
            page = await data.text()
        
    root = BeautifulSoup(page)

    try:
        # Get relevant sections of the HTML
        topic_entries  = root.find_all(class_='js-forum-topic-entry')
    
        topic_names    = [entry.find_all(class_='forum-topic-entry__title')[0] for entry in topic_entries]
        topic_authors  = [entry.find_all(class_='user-name js-usercard')[0] for entry in topic_entries]
        topic_lastPost = [[child.find_all(class_='user-name js-usercard')[0] for child in entry.find_all(class_='u-ellipsis-overflow')][0] for entry in topic_entries]
        topic_lastTime = [entry.find_all(class_='timeago')[0] for entry in topic_entries]

        # Extract data from HTML
        topic_names    = [name.text for name in topic_names]
        topic_authors  = [user.text for user in topic_authors]
        topic_lastPost = [user.text for user in topic_lastPost]
        topic_lastTime = [time.text for time in topic_lastTime]
    except:
         await message.channel.send("Something went wrong! Contact one of the bot devs.")
         print(subforum_url + " is no longer parsable :(")
         return

    # Validate to make sure everything matches up as expected
    if not (len(topic_names) == len(topic_authors) == len(topic_lastPost) == len(topic_lastTime)):
        await message.channel.send("Something went wrong! Contact one of the bot devs.")
        print("Data mismatch; topic_names: " + str(len(topic_names)) + "   topic_authors: " + str(len(topic_authors)) + "    topic_lastPost:" + str(len(topic_lastPost)) + "    topic_lastTime" + str(len(topic_lastTime)))
        return

    # process data
    topic_names    = [name.replace('\n', '') for name in topic_names]
    topic_lastPost = [pstr.replace('\n', '') for pstr in topic_lastPost]

    embed = discord.Embed(color=message.author.color)
    embed.add_field(name='Topic Name', value='\n'.join(topic_names), inline=True)
    embed.add_field(name='Topic Author', value='\n'.join(topic_authors))
    embed.add_field(name='Last post by', value='\n'.join(topic_lastPost))
    embed.add_field(name='Time', value='\n'.join(topic_lastTime))
    await message.channel.send(None, embed=embed)