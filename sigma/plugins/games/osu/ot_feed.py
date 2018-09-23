import asyncio
import discord
import socket
import json
import threading

from dateutil.parser import parse


class Connection():

    def __init__(self, ev, ip_addr, port):
        self.ev        = ev
        self.ip_addr   = ip_addr
        self.port      = port
        self.connected = False

        self.create_new_connection()
        

    def __del__(self):
        self.connection.close()


    def create_new_connection(self):
        try: 
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
            self.connection.settimeout(0.2)  # Time to wait (seconds) to revieve data from client every try
        except socket.error as err: 
            self.ev.log.info('socket creation failed with error %s' %(err))


    def handle_sudden_disconnect(self):
        self.connection.close()
        self.create_new_connection()
        self.connected = False
        self.ev.log.info('Disconnected from ' + self.ip_addr + ':' + str(self.port))


    async def connect_to_ot_forum_bot(self):
        while True:
            try: 
                self.connection.connect((self.ip_addr, self.port))
                self.connected = True
                self.ev.log.info('Connected to ' + self.ip_addr + ':' + str(self.port))
                break
            except socket.error as e: pass

            await asyncio.sleep(5)


    async def process_data(self):
        if not self.connected: return

        try:
            data = self.connection.recv(1024)
            if data == b'':
                self.handle_sudden_disconnect()
                return

        except socket.timeout: return   # If we timed out, sleep a bit and try again
        except socket.error as e: self.handle_sudden_disconnect()

        data = json.loads(data.decode('utf-8'))
        
        embed = discord.Embed(color=0x1ABC9C, timestamp=parse(data['time']))
        embed.set_author(name=data['user'], url=data['user_profile'], icon_url=data['avatar'])
        embed.add_field(name=data['thread_title'], value=data['post_url'])

        target_channels = [ channel for channel in [ channels for channels in [ server.channels for server in self.ev.bot.guilds ] ][0] if channel.name == 'ot-feed' ]
        for target_channel in target_channels:
            await target_channel.send(embed=embed)
            
            

async def ot_feed(ev):

    ip_addr = '127.0.0.1'
    port    = 55555

    ot_bot_connection = Connection(ev, ip_addr, port)
    client_thread     = threading.Thread(target=ot_bot_connection.process_data, args=())

    while True:
        await asyncio.sleep(1)

        if not ot_bot_connection.connected:
            await ot_bot_connection.connect_to_ot_forum_bot()
        
        await ot_bot_connection.process_data()
