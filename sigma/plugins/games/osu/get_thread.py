import discord
import aiohttp
import re
from bs4 import BeautifulSoup

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
        topic_name     = root.find_all(class_='link--white link--no-underline')
        topic_contents = root.find_all(class_='forum-post')

        post_authors  = [entry.find_all(class_='forum-post__username js-usercard')[0] for entry in topic_contents]
        post_ath_urls = [[avtr.get('href') for avtr in entry.find_all(class_='forum-post__username js-usercard')][0] for entry in topic_contents]
        post_avatars  = [[avtr.get('style') for avtr in entry.find_all(class_='avatar avatar--forum')][0] for entry in topic_contents]
        post_dates    = [entry.find_all(class_='timeago')[0] for entry in topic_contents]
        post_contents = [entry.find_all(class_='forum-post-content')[0] for entry in topic_contents]

        # Extract data from HTML
        subforum_name = [name.text for name in subforum_name][0]
        topic_name    = [name.text for name in topic_name][0]

        post_authors  = [auth.text for auth in post_authors]
        post_avatars  = [re.findall('background-image: url\(\'(.*?)\'\);', avtr)[0] for avtr in post_avatars]
        post_dates    = [date.text for date in post_dates]
        #post_contents = [data.text for data in post_contents]

    except:
        await channel.send("Something went wrong! Contact one of the bot devs.")
        cmd.log.error("[ get_thread ] " + topic_url + " is no longer parsable :(")
        return

    # Sanitize data
    subforum_name = subforum_name.replace('\n', '')
    topic_name    = topic_name.replace('\n', '')

    post_authors = [auth.replace('\n', '') for auth in post_authors]
    post_contents = [str(data).replace('\n','') for data in post_contents][0]

    post_contents = ''.join(post_contents)
    root = BeautifulSoup(post_contents, "lxml")

    # Process data
    root.div.unwrap()
    root.div.unwrap()

    while True:
        try:
            root.strong.insert_before("**")
            root.strong.insert_after("**")
            root.strong.unwrap()
        except: break

    while True:
        try:
            root.br.insert_before("\n")
            root.br.unwrap()
        except: break

    while True:
        try:
            root.ol.unwrap0()
        except: break

    while True:
        try:
            root.center.unwrap()
        except: break
   
    while True:
        try:
            root.li.insert_before("\n    ● ")
            root.li.unwrap()
        except: break

    while True:
        try:
            root.iframe.insert_before(root.iframe['src'])
            root.iframe.unwrap()
        except: break

    while True:
        try:
            root.em.insert_before('*')
            root.em.insert_after('*')
            root.em.unwrap()
        except: break

    while True:
        try:
            emoji = root.select_one("img.smiley")
            if emoji['title'] == 'smile': emoji.insert_after(':smile:')
            if emoji['title'] == 'wink': emoji.insert_after(':wink:')
            if emoji['title'] == 'Grin': emoji.insert_after(':grin:')
            if emoji['title'] == 'cry': emoji.insert_after(':cry:')
            emoji.unwrap()
        except: break

            root.img.unwrap()
        except: break

    while True:
        try:
            root.select_one("div.well").unwrap()
        except: break

    while True:
        try:
            root.select_one("i.fa.fa-chevron-down.bbcode-spoilerbox__arrow").insert_after('\n\n')
            root.select_one("i.fa.fa-chevron-down.bbcode-spoilerbox__arrow").unwrap()
        except: break

    while True:
        try:
            root.select_one("div.bbcode-spoilerbox__body").insert_before(': ')
            root.select_one("div.bbcode-spoilerbox__body").insert_after('\n')
            root.select_one("div.bbcode-spoilerbox__body").unwrap()
        except: break

    #print(root)
   
    post_contents = root.text
    post_contents = post_contents[:1024]

    # Post data
    embed = discord.Embed(type='rich', color=0x66CC66, title=subforum_name + ' > ' + topic_name)
    embed.set_author(name=post_authors[0], icon_url=post_avatars[0], url=post_ath_urls[0])
    if len(post_contents) != 0: 
        embed.add_field(name='___________', value=post_contents, inline=True)
    embed.set_footer(text=post_dates[0])
    await channel.send(None, embed=embed)




async def get_thread(cmd, message, args):

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    await display_thread(cmd, message.channel, args)

