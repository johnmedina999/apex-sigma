import discord
import asyncio
import aiohttp
from .get_thread import display_thread
from bs4 import BeautifulSoup

async def ot_feed(ev):

    forum_id = "52"
    check_topic_ids = [623207]
    latest_topic_id = 623207

    while True:
        for check_topic_id in check_topic_ids:

            # Delay not to spam requests
            await asyncio.sleep(5) 
            
            # Request website data
            try:
                subforum_url = "https://osu.ppy.sh/community/forums/topics/" + str(check_topic_id)
                async with aiohttp.ClientSession() as session:
                    async with session.get(subforum_url) as data:
                        page = await data.text()
            except Exception as e:
                ev.log.error("[ ot_feed ] Exception: " + str(e))
        
            # If page is not found, the topic is either removed or not yet made
            # Add to the topic ids to check for in case it is not yet made and start over from the beggining of the last
            if page.find("Page Missing") != -1 or page.find("You shouldn&#039;t be here.") != -1:    
                if (check_topic_id + 1) not in check_topic_ids:
                    check_topic_ids.append(check_topic_id + 1)
                    break             
            else:
                # That is our latest topic id and no need to check for any other but the next one
                check_topic_ids = [check_topic_id + 1]
                latest_topic_id = max(check_topic_id, latest_topic_id)

                OT_channels = [[channel for channel in guild.channels if channel.name == "ot-feed"][0] for guild in ev.bot.guilds]

                try:
                    for channel in OT_channels:
                        await channel.send("New topic id: " + str(check_topic_id))
                        await display_thread(channel, [str(check_topic_id)])
                except:
                   ev.log.error("[ ot_feed ] ERROR displaying post! Topic id: " + str(check_topic_id))