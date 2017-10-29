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
        topic_contents = root.find_all(class_='forum-post') # TODO: Use bbcode class instead

        post_authors  = [entry.find_all(class_='forum-post__username js-usercard')[0] for entry in topic_contents]
        post_ath_urls = [[avtr.get('href') for avtr in entry.find_all(class_='forum-post__username js-usercard')][0] for entry in topic_contents]
        post_avatars  = [[avtr.get('style') for avtr in entry.find_all(class_='avatar avatar--forum')][0] for entry in topic_contents]
        post_dates    = [entry.find_all(class_='timeago')[0] for entry in topic_contents]
        post_contents = root.find_all(class_='bbcode')[0]

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
    post_contents = str(post_contents).replace("*", "\*")

    # Process data
    root = BeautifulSoup(post_contents, "lxml")

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
            root.ol.unwrap()
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
            if root.img['data-normal']: root.img.insert_before(root.img['data-normal'].replace('http','img') + "\x03")
            elif root.img['src']:       root.img.insert_before(root.img['src'].replace('http','img') + "\x03")

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
            root.select_one("div.well").unwrap()
        except: break

    # TODO: Consider doing user quotes in code blocks. Not sure how nested quotes will do though

    # Compile embed contents
    post_contents = root.text
    posts = []; beg = 0; end = min(len(post_contents), beg + 1900)

    # Topic Header
    embed = discord.Embed(type='rich', color=0x66CC66, title=subforum_name + ' > ' + topic_name)
    embed.url = topic_url
    embed.set_author(name=post_authors[0], icon_url=post_avatars[0], url=post_ath_urls[0])
    posts.append(embed)

    '''
    # TODO: The special searches look for last thing within range and split posts regardless of whether more can fit
    '''
    # Split up fields in embed contents that are too long
    while True:
        idx = -1; state = 7

        if idx == -1:   # find first img
            idx = post_contents.find('img://', beg, end)    
            state = 1

        if idx == -1:   # find first img
            idx = post_contents.find('imgs://', beg, end)   
            state = 2

        if idx == -1:   # find last link
            idx = post_contents.rfind('http://', beg, end)  
            state = 3

        if idx == -1:   # find last link
            idx = post_contents.rfind('https://', beg, end) 
            state = 4

        if idx == -1:   # find last newline
            idx = post_contents.rfind('\n', beg, end)      
            state = 5

        if idx == -1:   # find last space
            idx = post_contents.rfind(' ', beg, end)        
            state = 6

#        print("state: " + str(state) + "  beg: " + str(beg) + "  idx: " + str(idx) + "  end: " + str(end) + "  len: " +  str(len(post_contents)) + "  thread: " + str(thread_id))
#        input()

        # if it's an image, get everything prior first to then get just the image
        if state <= 2 and beg != idx: 
            end = idx; continue

        # The \x03 is used to indicate the end of a link. If link is too big, get everything prior to it first
        if state <= 4:
            end_link = post_contents.find('\x03', idx, end)
            if end_link >= 2000: end = idx; continue
            idx = end_link

        embed = discord.Embed(type='rich', color=0x66CC66)
        
        if state <= 2: embed.set_image(url=post_contents[beg:idx].replace('img','http'))  # process img
        elif state <= 4: embed.description = post_contents[beg:idx]                       # process link
        else: embed.description = post_contents[beg:end]                                  # process normal text
        
        posts.append(embed)

#        print("beg: " + str(beg) + " -> " + str(idx))
#        print("end: " + str(end) + " -> " + str(min(len(post_contents), beg + 1900)))
        
        # If search found nothing of interest, then we can take the rest of the post
        # Otherwise, continue off from the end of the previous point of interest
        if idx == -1: beg = end
        else: beg = idx + 1

        # if this is true, then it printed the rest of the stuff
        if state >= 5 and end == len(post_contents): break
        
        # update the end; split it up by 1900 characters or the size of the post, whatev is smaller
        end = min(len(post_contents), beg + 1900)

        # Nothing to do if we are going to search an empty string
        if beg == end: break
        
    # TODO: img tags now just have img with no attributes
    # TODO: forum links now are wrapped in "postlink" class

    # TODO: Threads to fix:
    #   626754 - Error displaying post (due to change in HTML relating to forum links)
    #   626684 - Chopped off formatted link
    #   626705 - Random ** bold formatting markers
    #   626710 - Collapsed text spoiler shows
    #   626725 - Chopped off formatted link
    #   627136 - Formatting error with URL
    #   629614 - Token parser messes up link
    #   629936 - markdown formatting error

    for post in posts:
         await channel.send(None, embed=post)
         await asyncio.sleep(1) # Delay so that the posts don't get shuffled later on


async def get_thread(cmd, message, args):

    if len(args) < 1:
        await message.channel.send(cmd.help())
        return

    await display_thread(cmd, message.channel, args)

