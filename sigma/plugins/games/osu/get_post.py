import discord
import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup

from .misc.BBcodeProcessor.BBcodeProcessor import BBcodeProcessor
from .misc.BBcodeProcessor.DiscordBBcodeCompiler import DiscordBBcodeCompiler
from .misc.Forum.Structs.Topic import Topic
from .misc.Forum.Structs.User import User
from .misc.Forum.Structs.Post import Post

async def display_post(cmd, channel, args):

    post_id = get_post_id(args[0])
    
    # Get the HTML page
    topic_url = 'https://osu.ppy.sh/community/forums/posts/' + post_id
    async with aiohttp.ClientSession() as session:
        async with session.get(topic_url) as data:
            page = await data.text()

    if page.find("Page Missing") != -1 or page.find("You shouldn&#039;t be here.") != -1:
        await channel.send("Post does not exist! Maybe you wanted to get by topic instead? (>>get_topic)")
        return

    root  = BeautifulSoup(page, "lxml")
    topic = Topic(root)

    try:
        subforum_name       = topic.getSubforum()
        topic_name          = topic.getName()
        topic_poster_name   = topic.getCreator().getName()
        topic_poster_avatar = topic.getCreator().getAvatar()
        topic_poster_url    = topic.getCreator().getUrl()

        post_contents      = None
        post_poster_name   = None
        post_poster_avatar = None
        post_poster_url    = None
        target_url         = 'https://osu.ppy.sh/community/forums/posts/' + str(post_id)

        for post in topic.getPosts():
            if post.getUrl() == target_url:
                post_contents      = post.getContents()
                post_poster_name   = post.getCreator().getName()
                post_poster_avatar = post.getCreator().getAvatar()
                post_poster_url    = post.getCreator().getUrl()
    except:
        await channel.send("Something went wrong! Contact one of the bot devs.")
        cmd.log.error("[ get_post ] " + topic_url + " is no longer parsable :(")
        return

    # Sanitize data
    topic_name = topic_name.replace('\n', '').replace(']', '\]')

    # Compile embed contents
    post_contents = BBcodeProcessor().Process(post_contents).text
    posts = []

    # Topic Header
    embed = discord.Embed(type='rich', color=0x66CC66, title=subforum_name + ' > ' + topic_name)
    embed.url = topic_url
    embed.set_author(name=topic_poster_name, icon_url=topic_poster_avatar, url=topic_poster_url)
    posts.append(embed)

    DiscordBBcodeCompiler().Compile(post_contents, posts)
    posts[1].set_author(name=post_poster_name, icon_url=post_poster_avatar, url=post_poster_url)

    # Post everything to discord
    for post in posts:
        await channel.send(None, embed=post)
        await asyncio.sleep(1) # Delay so that the posts don't get shuffled later on


def get_post_id(arg):
    token = 'https://osu.ppy.sh/community/forums/topics/'
    idx = arg.find(token)
    if idx != -1:
        token = '?start='
        idx = arg.find(token)

        if idx != -1: return arg[idx:]

    token = 'https://osu.ppy.sh/community/forums/posts/'
    idx = arg.find(token)
    if idx != -1: return arg[len(token):]

    token = 'https://osu.ppy.sh/forum/p/'
    idx = arg.find(token)
    if idx != -1: return arg[len(token):]

    return arg


async def get_post(cmd, message, args):
    args = [arg for arg in args if arg != '']

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    await display_post(cmd, message.channel, args)
