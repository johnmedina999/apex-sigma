import asyncio
import discord
import arrow

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

spam_info = {}
message_sample = {}
prev_time = arrow.utcnow().timestamp


def add_to_message_sample(ev, message):
    global message_sample           # Contains spam_sample_time's worth of message from all channels in all guilds

    try: message_sample[message.guild.id][message.channel.id].append(message)
    except:
        try: message_sample[message.guild.id][message.channel.id] = [ message ]
        except:
            try:
                message_sample[message.guild.id] = {}
                message_sample[message.guild.id][message.channel.id] = [ message ]
            except: ev.log.info('[SPAM MONITOR] Unable to record message sample for ' + message.channel.name + ' in ' + message.guild.name)


# Tier 0: Do nothing; Everything is ok
# Tier 1: Delete spam messages
#         At some point if the messages are coming in fast enough, the bot would have trouble deleting them
#         Escalate to tier 2 if that's the case
# Tier 2: If there are successive repeated spam detections, remove ability to send messages for 1 minute
# Tier 3: Start banning users
# Tier 4: Revoke invite keys
#         Possibly escalate to Tier 4 if it sees a spike of invites and there is spam

def add_to_spam_info(ev, guild_id, channel_id):
    global spam_info                # Contains how persistant spam is on a server (persistance, tier)

    try:
        if spam_info[guild_id][channel_id][0] == 3:
            spam_info[guild_id][channel_id][0] = 0
            spam_info[guild_id][channel_id][1] += 1
        else:
            spam_info[guild_id][channel_id][0] += 1
    except:
        try: spam_info[guild_id][channel_id] = [0, 1]
        except:
            try: 
                spam_info[guild_id] = {}
                spam_info[guild_id][channel_id] = [0, 1]
            except: 
                ev.log.info('[SPAM MONITOR] Unable to record spam info for channel id ' + channel_id + ' in guild id' + guild_id)


async def spam_monitor(ev, message, args):
    if not message.guild: return    # Don't process messages recieved privately

    global message_sample           # Contains spam_sample_time's worth of message from all channels in all guilds
    global spam_info                # Contains how persistant spam is on a server
    global prev_time                # This is in seconds

    # Keep track number of messages in every channel of every server per spam sample time
    add_to_message_sample(ev, message)

    # If timer has not expired, it's early to go through messages
    if arrow.utcnow().timestamp <= prev_time + SpamSampleTime: return
        
    for guild_id, guild_sample in message_sample.items():
        for channel_id, channel_sample in guild_sample.items():
            
            # If number of messages don't exceed spam threshold, then reset persistance
            if not len(channel_sample) >= ev.db.get_settings(guild_id, 'SpamThreshold'): 
                try: del spam_info[guild_id][channel_id]
                except: pass
                continue

            add_to_spam_info(ev, guild_id, channel_id)
            persistance = spam_info[guild_id][channel_id][0]
            tier = spam_info[guild_id][channel_id][1]

            # TIER actions for severity detection
            if tier >= 1: await message.channel.delete_messages(channel_sample)
            if tier >= 2: 
                if persistance == 1:
                    embed = discord.Embed(title=':bat: Stop Spamming!!! :bat:', color=0xDBD000)
                    await channel_sample[0].channel.send(None, embed=embed)
            if tier >= 3: 
                # TODO: Remove message post permission from everyone in the channel
                # TODO: Send warns to all people that spammed
                pass
            if tier >= 4: 
                # TODO: Revoke invite links
                pass
        
            users_info = ', '.join([ message.author.name for message in channel_sample ])
            ev.log.info('[SPAM MONITOR] TIER ' + str(tier) + ' - Channel Detected: ' + channel_sample[0].channel.name + ' in ' + channel_sample[0].guild.name + '\n' \
                        '\t Users: ' + users_info)

            # Notify mod channel
            try:
                mod_notifications_enabled = ev.db.get_settings(guild_id, 'ModeratorNotifications')
                if not mod_notifications_enabled: continue
                    
                modchannel_id = ev.db.get_settings(guild_id, 'ModeratorChannel')
                modchannel    = discord.utils.find(lambda c: c.id == modchannel_id, channel_sample[0].guild.channels)
            
                embed = discord.Embed(title='TIER ' + str(tier) + ' SPAM EVENT DETECTED', color=0xDB0000)
                embed.add_field(name='Channel: ', value=channel_sample[0].channel.name)
                embed.add_field(name='Action Taken: ', value='Deleted Messages')
                embed.add_field(name='Users: ', value=users_info)
                await modchannel.send(None, embed=embed)

                if tier == 2 and persistance == 2:
                    await modchannel.send(":bat: @here AHHHH!!! Where are the mods??? Help me!!!")
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
