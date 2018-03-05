import asyncio
import discord
import arrow

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
    if not message.guild: return

    spam_threshold = 15                     # TODO: Put this in config.py
    spam_sample_time = 3                    # TODO: put this in config.py (seconds)

    global message_sample
    global prev_time
    global tier

    if arrow.utcnow().timestamp > prev_time + spam_sample_time:    # This is in seconds
        for guild_id, guild_sample in message_sample.items():
            for channel_id, channel_sample in guild_sample.items():        
                if len(channel_sample) > spam_threshold:
                    #for message in channel_sample:
                    #    print('User Joined: ' + str(message.author.created_at) + '   Channel Detected: ' + str(message.channel.name) + ' in ' + str(message.guild.name))
                    print('spam event detected')
                    await message.channel.delete_messages(channel_sample)
        #               if message.author.created_at > arrow.utcnow().timestamp - one_Hour:
        #                  lets not do that yet... instead, just alert admin channel about user if hadn't alerted before ---> ban user
        #                   delete message
        #
        #   if tier >= 4:
        #       if guild_id in flagged_guilds:      # If this is the guild that is having spam issues
        #           ev.db.set_settings(guild_id, 'BlockInvites', True)
        #           embed = discord.Embed(color=0x66CC66, title=':white_check_mark: Invite Blocking Has Been Enabled')
        #           await admin_channel.send(None, embed=embed)  # send alert to admin channel
        
        message_sample = {}
        prev_time = arrow.utcnow().timestamp
    
    else:
        if not message_sample:
            message_sample[message.guild.id] = {}
            message_sample[message.guild.id][message.channel.id] = [ message ]
        elif not message_sample[message.guild.id]:
            message_sample[message.guild.id][message.channel.id] = [ message ]
        else:
            if message in message_sample[message.guild.id][message.channel.id]: return
            message_sample[message.guild.id][message.channel.id].append(message)
