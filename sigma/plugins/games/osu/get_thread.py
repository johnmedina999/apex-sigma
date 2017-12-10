import discord
import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup
from .BBcodeProcessor.BBcodeProcessor import BBcodeProcessor
from .BBcodeProcessor.DiscordBBcodeCompiler import DiscordBBcodeCompiler

async def display_thread(cmd, channel, args):

    thread_id = args[0]

    # Get the HTML page
    topic_url = 'https://osu.ppy.sh/community/forums/topics/' + thread_id
    async with aiohttp.ClientSession() as session:
        async with session.get(topic_url) as data:
            page = await data.text()

    if page.find("Page Missing") != -1 or page.find("You shouldn&#039;t be here.") != -1:
        await channel.send("Topic does not exist!")
        return

    root = BeautifulSoup(page, "lxml")

    try:
        # Get relevant sections of the HTML
        subforum_name  = root.find_all(class_='page-mode-link--is-active')
        topic_name     = root.find_all(class_='js-forum-topic-title--title')
        topic_contents = root.find_all(class_='forum-post')
        post_dates     = [entry.find_all(class_='timeago')[0] for entry in topic_contents]
        post_contents  = root.find_all(class_='forum-post-content ')
        posters        = root.find_all(class_='forum-post__info-panel')

        # Not all users have urls, avatars, etc in their profile (restricted users)
        poster_urls = []; poster_avatars = []; poster_names = []
        
        for poster in posters:
            try: poster_name = poster.find_all(class_='forum-post__username')[0]
            except: poster_name = ""
            if not poster_name: poster_name = ""

            try: poster_url = poster.find_all(class_='forum-post__username')[0].get('href')
            except: poster_url = "https://osu.ppy.sh/users/-1"
            if not poster_url: poster_url = "https://osu.ppy.sh/users/-1"
            
            try: poster_avatar = poster.find_all(class_='avatar avatar--forum')[0].get('style')
            except: poster_avatar = "background-image: url('');"
            if not poster_avatar: poster_avatar = "background-image: url('');"

            poster_names.append(poster_name)
            poster_urls.append(poster_url)
            poster_avatars.append(poster_avatar)

        # Extract data from HTML
        post_contents  = post_contents[0]
        subforum_name  = [name.text for name in subforum_name][0]
        topic_url      = [name['href'] for name in topic_name][0]
        topic_name     = [name.text for name in topic_name][0]
        post_dates     = [date.text for date in post_dates]
        poster_names   = [auth.text for auth in poster_names]
        poster_avatars = [re.findall('background-image: url\(\'(.*?)\'\);', avtr)[0] for avtr in poster_avatars]

    except:
        await channel.send("Something went wrong! Contact one of the bot devs.")
        cmd.log.error("[ get_thread ] " + topic_url + " is no longer parsable :(")
        return


    # Sanitize data
    subforum_name = subforum_name.replace('\n', '')
    topic_name    = topic_name.replace('\n', '').replace(']', '\]')
    topic_url     = topic_url.replace(')', '\)')
    poster_names  = [auth.replace('\n', '') for auth in poster_names]
    post_contents = str(post_contents).replace('*', '\*')
    # \TODO: sanitize the tokens used to identify images and links below


    # Compile embed contents
    post_contents = BBcodeProcessor().Process(post_contents).text
    posts = []

    # Topic Header
    embed = discord.Embed(type='rich', color=0x66CC66, title=subforum_name + ' > ' + topic_name)
    embed.url = topic_url
    embed.set_author(name=poster_names[0], icon_url=poster_avatars[0], url=poster_urls[0])
    posts.append(embed)

    posts = DiscordBBcodeCompiler().Compile(post_contents, posts)

        
    # TODO: img tags now just have img with no attributes
    # TODO: forum links now are wrapped in "postlink" class
    # TODO: Take account formatting when splitting. Stuff like bold sentences get 
    #       split up, and are displayed incorrectly (asterisks visible on both ends)
    # TODO: Quote styling http://i.imgur.com/ysgOpcz.png


    # TODO: Threads to fix:
    #   626816 - Got stuck
    #   626799 - Something wrong with this
    #   626763 - Exceeded discord length limit
    #   626684 - Can maybe be split up less
    #   626710 - Collapsed text spoiler shows
    #   627136 - Formatting error with URL; Got stuck

    # Post everything to discord
    for post in posts:
         await channel.send(None, embed=post)
         await asyncio.sleep(1) # Delay so that the posts don't get shuffled later on


async def get_thread(cmd, message, args):

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    await display_thread(cmd, message.channel, args)

