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
    poster_names = [auth.replace('\n', '') for auth in poster_names]
    post_contents = str(post_contents).replace("*", "\*")

    # Process data
    root = BeautifulSoup(post_contents, "lxml")

    while True:
        try: # Bold text
            if root.strong.get_text():
                root.strong.insert_before('**')
                root.strong.insert_after('**')
            root.strong.unwrap()
        except: break

    while True:
        try: # Next lines
            root.br.insert_before('\n')
            root.br.unwrap()
        except: break

    while True:
        try: # List indicator; ignore
            root.ol.unwrap()
        except: break

    while True:
        try: # Can't do centered text in discord well; ignore
            root.center.unwrap()
        except: break
   
    while True:
        try: # List bullets
            if root.strong.get_text():
                root.li.insert_before('\n    ● ')
            root.li.unwrap()
        except: break

    while True:
        try: # Replace https with vid so we can easily identify Youtube video links later on
            root.iframe.insert_before(root.iframe['src'].replace('http','vid') + '\x03')
            root.iframe.unwrap()
        except: break

    while True:
        try: # Italic text
            if root.strong.get_text():
                root.em.insert_before('*')
                root.em.insert_after('*')
            root.em.unwrap()
        except: break

    while True:
        try: # Spoiler box arrow
            root.select_one("i.fa.fa-chevron-down.bbcode-spoilerbox__arrow").insert_after('\n')
            root.select_one("i.fa.fa-chevron-down.bbcode-spoilerbox__arrow").unwrap()
        except: break

    while True:
        try: # Spoiler box open/close thingy
            root.select_one("div.bbcode-spoilerbox__body").insert_before(':\n ')
            root.select_one("div.bbcode-spoilerbox__body").insert_after('\n')
            root.select_one("div.bbcode-spoilerbox__body").unwrap()
        except: break

    while True:
        try: # Emojis
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
            if root.img['data-normal']: root.img.insert_before(root.img['data-normal'].replace('http','img') + '\x03')
            elif root.img['src']:       root.img.insert_before(root.img['src'].replace('http','img') + '\x03')

            root.img.unwrap()
        except: break

    while True:
        try: # Add markdown for it to be a hyperlink
            try: root.a.insert_before('[' + root.a.text.replace(']', '\]') + ']' + '(' + root.a['href'].replace(')', '\)') + ')\x03')
            except: pass

            root.a.clear()
            root.a.unwrap()
        except: break

    while True:
        try:
            root.select_one("div.well").insert_before('\n\n')
            root.select_one("div.well").unwrap()
        except: break

    # TODO: Consider doing user quotes in code blocks. Not sure how nested quotes will do though

    # Compile embed contents
    post_contents = root.text
    buffer_size = 2048
    posts = []; beg = 0

    # Topic Header
    embed = discord.Embed(type='rich', color=0x66CC66, title=subforum_name + ' > ' + topic_name)
    embed.url = topic_url
    embed.set_author(name=poster_names[0], icon_url=poster_avatars[0], url=poster_urls[0])
    posts.append(embed)

    # Process posts. Need to split them up due to discord lenth limits
    while True:
               
        end = min(len(post_contents), beg + buffer_size)
        if beg >= end: break

        embed = discord.Embed(type='rich', color=0x66CC66)
        buffer = post_contents[beg:end]

        #input()
        #print("beg: " + str(beg) + "  end: " + str(end) + "  len: " +  str(len(post_contents)) + "  thread: " + str(thread_id))
        
        # If found, then check if there is something to record before that
        idx = buffer.find('img://', 0, len(buffer))
        if idx != -1:
            #print("img")
            if idx == 0:
                idx = buffer.find('\x03', 0, end)
                embed.set_image(url=buffer[0:idx].replace('img','http'))
            else:
                embed.description = buffer[0:idx].replace('\x03','').strip()
                posts.append(embed)

            beg += idx
            continue

        # If found, then check if there is something to record before that
        idx = buffer.find('imgs://', 0, len(buffer))
        if idx != -1: 
            #print("imgs")
            if idx == 0: # Record img
                idx = buffer.find('\x03', 0, end)
                embed.set_image(url=buffer[0:idx].replace('imgs','https'))
                #print(buffer[0:idx])
                posts.append(embed)
            else:
                embed.description = buffer[0:idx].replace('\x03','').strip()
                posts.append(embed)
            
            beg += idx
            continue

        # If found, then see if we can get the link's end. If not, get everything prior
        idx = buffer.rfind('vids://', 0, len(buffer))
        if idx != -1:
            #print("vids")
            link_end = buffer.rfind('\x03', 0, end)
            if link_end != -1: idx = link_end

            embed.description = buffer[0:idx].replace('vids','https').replace('\x03','').strip()
            posts.append(embed)
            beg += idx
            continue

        # If the post fits well below the lenth, just record it. 
        # Otherwise, start looking at the best way to split it up
        if len(buffer) < (buffer_size - 200):
            #print("just recorded")
            embed.description = buffer[0:len(buffer)].replace('\x03','').strip()
            posts.append(embed)
            beg += len(buffer)
            continue

        # If found, then see if we can get the link's end. If not, get everything prior
        idx = buffer.rfind('http://', 0, len(buffer))
        if idx != -1: 
            #print("http")
            link_end = buffer.rfind('\x03', 0, end)
            if link_end != -1: idx = link_end

            embed.description = buffer[0:idx].replace('\x03','').strip()
            posts.append(embed)
            beg += idx
            continue

        # If found, then see if we can get the link's end. If not, get everything prior
        idx = buffer.rfind('https://', 0, len(buffer))
        if idx != -1:
            #print("https")
            link_end = buffer.rfind('\x03', 0, end)
            if link_end != -1: idx = link_end

            embed.description = buffer[0:idx].replace('\x03','').strip()
            posts.append(embed)
            beg += idx
            continue

        # If found, then record the range
        idx = buffer.rfind('\n', 0, len(buffer))
        if idx != -1:
            #print("NL")
            embed.description = buffer[0:idx].replace('\x03','').strip()
            posts.append(embed)
            beg += idx + 1
            continue

        # If found, then record the range
        idx = buffer.rfind(' ', 0, len(buffer))
        if idx != -1: 
            #print("space")
            embed.description = buffer[0:idx].replace('\x03','').strip()
            posts.append(embed)
            beg += idx + 1
            continue

        # If all else fails
        #print("any")
        embed.description = buffer.replace('\x03','').strip()
        posts.append(embed)
        beg += len(buffer)

        
    # TODO: img tags now just have img with no attributes
    # TODO: forum links now are wrapped in "postlink" class

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

