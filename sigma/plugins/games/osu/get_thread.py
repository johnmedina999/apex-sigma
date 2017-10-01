import discord
import aiohttp
import asyncio
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
        topic_contents = root.find_all(class_='forum-post') # TODO: Use bbcode class instead

        post_authors  = [entry.find_all(class_='forum-post__username js-usercard')[0] for entry in topic_contents]
        post_ath_urls = [[avtr.get('href') for avtr in entry.find_all(class_='forum-post__username js-usercard')][0] for entry in topic_contents]
        post_avatars  = [[avtr.get('style') for avtr in entry.find_all(class_='avatar avatar--forum')][0] for entry in topic_contents]
        post_dates    = [entry.find_all(class_='timeago')[0] for entry in topic_contents]
        post_contents = [entry.find_all(class_='forum-post-content')[0] for entry in topic_contents]

        # Extract data from HTML
        subforum_name = [name.text for name in subforum_name][0]
        topic_url     = [name['href'] for name in topic_name][0]
        topic_name    = [name.text for name in topic_name][0]
        post_authors  = [auth.text for auth in post_authors]
        post_avatars  = [re.findall('background-image: url\(\'(.*?)\'\);', avtr)[0] for avtr in post_avatars]
        post_dates    = [date.text for date in post_dates]

    except:
        await channel.send("Something went wrong! Contact one of the bot devs.")
        cmd.log.error("[ get_thread ] " + topic_url + " is no longer parsable :(")
        return

    # Sanitize data
    subforum_name = subforum_name.replace('\n', '')
    topic_name    = topic_name.replace('\n', '').replace(']', '\]')
    topic_url     = topic_url.replace(')', '\)')

    post_authors = [auth.replace('\n', '') for auth in post_authors]
    post_contents = [str(data).replace('\n','') for data in post_contents][0]

    post_contents = ''.join(post_contents)
    root = BeautifulSoup(post_contents, "lxml")

    # Process data
    root.div.unwrap()
    root.div.unwrap()

    while True:
        try: # Bold text
            root.strong.insert_before("**")
            root.strong.insert_after("**")
            root.strong.unwrap()
        except: break

    while True:
        try: # Next lines
            root.br.insert_before("\n")
            root.br.unwrap()
        except: break

    while True:
        try: # List indicator; ignore
            root.ol.unwrap0()
        except: break

    while True:
        try: # Can't do centered text in discord well; ignore
            root.center.unwrap()
        except: break
   
    while True:
        try: # List bullets
            root.li.insert_before("\n    ● ")
            root.li.unwrap()
        except: break

    while True:
        try: # Youtube video; Consider making this its own post if it's possible to embed like pictures
            root.iframe.insert_before(root.iframe['src'])
            root.iframe.unwrap()
        except: break

    while True:
        try: # Italic text
            root.em.insert_before('*')
            root.em.insert_after('*')
            root.em.unwrap()
        except: break

    while True:
        try: # Spoiler box arrow
            emoji = root.select_one("img.smiley")
            if emoji['title'] == 'smile': emoji.insert_after(':smile:')
            if emoji['title'] == 'wink': emoji.insert_after(':wink:')
            if emoji['title'] == 'Grin': emoji.insert_after(':grin:')
            if emoji['title'] == 'cry': emoji.insert_after(':cry:')
            emoji.unwrap()
        except: break

    while True:
        try: # Images
            
            try: # For any missed emoji
                if root.img['class'] == ['smiley']: 
                    cmd.log.warning("[ get_thread ] Smiley not handled: " + root.img)
                    root.img.unwrap()
                    continue
            except: pass

            # Replace https with img so we can easily identify image links later on
            if root.img['data-normal']: root.img.insert_before(root.img['data-normal'].replace('https','img') + " ")
            elif root.img['src']:       root.img.insert_before(root.img['src'].replace('https','img') + " ")

            root.img.unwrap()
        except: break

    while True:
        try: # Add markdown for it to be a hyperlink
            try: root.a.insert_before('[' + root.a.text.replace(']', '\]') + ']' + '(' + root.a['href'].replace(')', '\)') + ')')
            except: pass

            root.a.clear()
            root.a.unwrap()
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
    links = [match.start() for match in re.finditer(re.escape("img://"), post_contents)]
    link_end = 0
    posts = []

    # Compile embed contents
    embed = discord.Embed(type='rich', color=0x66CC66, title=subforum_name + ' > ' + topic_name)
    embed.url = topic_url
    embed.set_author(name=post_authors[0], icon_url=post_avatars[0], url=post_ath_urls[0])
    posts.append(embed)
   
    for link in links:
        if len(post_contents[link_end:link].strip()) != 0:
            embed = discord.Embed(type='rich', color=0x66CC66)
            embed.description += post_contents[link_end:link]
            posts.append(embed)

        # Images are their own post
        link_end = post_contents[link:].find(' ') + link
        embed = discord.Embed(type='rich', color=0x66CC66)
        embed.set_image(url=post_contents[link:link_end].replace('img','https'))
        posts.append(embed)

    embed = discord.Embed(type='rich', color=0x66CC66)
    if len(post_contents[link_end:len(post_contents)].strip()) != 0:
        embed.add_field(name='___________', value=post_contents[link_end:len(post_contents)], inline=False)
    embed.set_footer(text=post_dates[0])
    posts.append(embed)

    # Split up fields in embed contents that are too long
    for post in posts:
        if len(post.fields) > 0:
            if len(post.fields[0].value) > 1024:
                split_posts = [post.fields[0].value[part:part+1024] for part in range(0, len(post.fields[0].value), 1024)]
                post.remove_field(0)
                for split in split_posts:
                    post.add_field(name='___________', value=split, inline=False)


    # TODO: Make sure links are intact during the splitting process

    for post in posts:
         await channel.send(None, embed=post)
         await asyncio.sleep(1) # Delay so that the posts don't get shuffled later on


async def get_thread(cmd, message, args):

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    await display_thread(cmd, message.channel, args)

