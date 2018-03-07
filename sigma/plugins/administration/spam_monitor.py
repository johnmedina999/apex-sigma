import asyncio
import discord
import arrow

from config import SpamThreshold
from config import SpamSampleTime

''' Format:
{
    server : { 
        channel : [ message, message, ... ],
        channel : [ message, message, ... ],
        ...
    },
    server : { 
        channel : [ message, message, ... ],
        channel : [ message, message, ... ],
        ...
    },
    ....
}
'''
message_sample = {}
prev_time = arrow.utcnow().timestamp

# Tier 0: Do nothing; Everything is ok
# Tier 1: Delete spam messages
#         At some point if the messages are coming in fast enough, the bot would have trouble deleting them
#         Escalate to tier 2 if that's the case
# Tier 2: If there are successive repeated spam detections, remove ability to send messages for 1 minute
# Tier 3: Start banning users
# Tier 4: Revoke invite keys
#         Possibly escalate to Tier 4 if it sees a spike of invites and there is spam
tier = 0

async def spam_monitor(ev, message, args):
    if not message.guild: return    # Don't process messages recieved privately

    global message_sample           # Contains spam_sample_time's worth of message from all channels in all guilds
    global prev_time                # This is in seconds
    global tier                     # For severity detection

    # Add new message into sample
    if not message_sample:
        message_sample[message.guild.id] = {}
        message_sample[message.guild.id][message.channel.id] = [ message ]
    elif not message_sample[message.guild.id]:
        message_sample[message.guild.id][message.channel.id] = [ message ]
    else:
        if message not in message_sample[message.guild.id][message.channel.id]:
            message_sample[message.guild.id][message.channel.id].append(message)

    # If timer has not expired, it's early to go through messages
    if arrow.utcnow().timestamp <= prev_time + SpamSampleTime: return
        
    for guild_id, guild_sample in message_sample.items():
        for channel_id, channel_sample in guild_sample.items():        
            if not len(channel_sample) >= SpamThreshold: continue   # If number of messages don't exceed spam threshold, then nothing more to do
            
            # TIER 1 action
            await message.channel.delete_messages(channel_sample)
            
            users_info = ', '.join([ message.author.name for message in channel_sample ])
            ev.log.info('[SPAM MONITOR] TIER 1 - Channel Detected: ' + channel_sample[0].channel.name + ' in ' + channel_sample[0].guild.name + '\n' \
                        '\t Users: ' + users_info)
            #for message in channel_sample:
            #    print('User Joined: ' + str(message.author.created_at) + '   Channel Detected: ' + str(message.channel.name) + ' in ' + str(message.guild.name))
                
            # Notify mod channel
            try:
                mod_notifications_enabled = ev.db.get_settings(guild_id, 'ModeratorNotifications')
                if not mod_notifications_enabled: continue
                    
                modchannel_id = ev.db.get_settings(guild_id, 'ModeratorChannel')
                modchannel    = discord.utils.find(lambda c: c.id == modchannel_id, channel_sample[0].guild.channels)
            
                embed = discord.Embed(title='TIER 1 SPAM EVENT DETECTED', color=0xDB0000)
                embed.add_field(name='Channel: ', value=channel_sample[0].channel.name)
                embed.add_field(name='Users: ', value=users_info)
                await modchannel.send(None, embed=embed)
            except:
                ev.log.info('[SPAM MONITOR] No moderator notification sent because server named ' + channel_sample[0].guild.name + \
                            ' does not have a moderator channel set up')

    #       if message.author.created_at > arrow.utcnow().timestamp - one_Hour:
    #           lets not do that yet... instead, just alert admin channel about user if hadn't alerted before ---> ban user
    #           delete message
    #
    #   if tier >= 4:
    #       if guild_id in flagged_guilds:      # If this is the guild that is having spam issues
    #           ev.db.set_settings(guild_id, 'BlockInvites', True)
    #           embed = discord.Embed(color=0x66CC66, title=':white_check_mark: Invite Blocking Has Been Enabled')
    #           await admin_channel.send(None, embed=embed)  # send alert to admin channel
        
    # Reset sample
    message_sample = {}
    prev_time = arrow.utcnow().timestamp
