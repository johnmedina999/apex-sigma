import asyncio
import discord
import json

from sigma.core.data_reciever import DataReciever
from dateutil.parser import parse


class DataHandler():
    
    @staticmethod
    async def handle_data(data, ev):
        new_link = 'https://osu.ppy.sh/community/forums/posts/' + data['post_id']
        old_link = 'https://old.ppy.sh/forum/p/' + data['post_id']

        avatar_url = data['avatar'] if data['avatar'] != '' else discord.Embed.Empty
        user_url   = data['user_profile'] if data['user_profile'] != '' else discord.Embed.Empty

        embed = discord.Embed(color=0x1ABC9C, timestamp=parse(data['time']))
        embed.set_author(name=data['user'], url=user_url, icon_url=avatar_url)
        embed.add_field(name=data['thread_title'], value=new_link + '\n' + old_link)

        try:
            for server in ev.bot.guilds:
                for channel in server.channels:
                    if channel.name == 'ot-feed':
                        await channel.send(embed=embed)
        except Exception as e:
            ev.log.error('Unable to send message to ot-feed;\n' + str(data) + '\n' + str(e))



async def ot_feed(ev):
    data_reciever = DataReciever(55555, DataHandler.handle_data)
    while True:
        await asyncio.sleep(0.1)
        await data_reciever.read_data((ev,))
