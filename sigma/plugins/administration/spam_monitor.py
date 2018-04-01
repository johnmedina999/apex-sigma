import asyncio
import discord
import arrow

from .spam.spam_data import SpamInfo, MessageInfo
from .spam.spam_actions import post_to_mod_channel, tier_actions_begin, tier_actions_end
from config import SpamSampleTime


spam_info      = SpamInfo()
message_sample = MessageInfo()


async def spam_monitor(ev, message, args):
    if not message.guild: return    # Don't process messages recieved privately

    global message_sample           # Contains spam_sample_time's worth of message from all channels in all guilds
    global spam_info                # Contains how persistant spam is on a server

    guild_id   = message.guild.id
    channel_id = message.channel.id
    location   = (ev, guild_id, channel_id)

    # Skip processing if the channel is muted due to spamming; It's being processed in another task
    if spam_info.get_muted_status(*location): return

    # Keep track number of messages in every channel of every server per spam sample time
    message_sample.add_to_message_sample(ev, message)

    # If not enough time has passed, then there is nothing to do
    prev_time = spam_info.get_check_time(*location)
    if arrow.utcnow().timestamp <= prev_time + SpamSampleTime: return
    
    channel_sample = message_sample.get_message_sample(guild_id, channel_id)
    spam_threshold = ev.db.get_settings(guild_id, 'SpamThreshold')

    # If number of messages don't exceed spam threshold, within the sample time,
    # then reset tier & persistance and clear message sample
    if len(channel_sample) < spam_threshold: 
        try: 
            spam_info.reset_info(*location)
            message_sample.reset_info(*location)
        except: pass
        return
    

    ######################################################
    ##   Prcessing
    ######################################################

    #print('Handeling spam...')
    spam_info.add_info(*location)
    spam_info.update_check_time(*location)

    persistance = spam_info.get_persistance(*location)
    tier        = spam_info.get_spam_tier(*location)
    #print('Channel: ' + message.channel.name + ' Tier: ' + str(tier) + ' Persistance: ' + str(persistance))
    
    # 100 msgs is max it can delete at once
    if len(channel_sample) > 75 and tier < 3:
        spam_info.set_spam_tier(*location, tier=3)      # Auto escalation as panic response


    ######################################################
    ##   Notifications
    ######################################################

    users_info = ', '.join([ message.author.name for message in channel_sample ])
    ev.log.info('[SPAM MONITOR] TIER ' + str(tier) + ' - Channel Detected: ' + channel_sample[0].channel.name + ' in ' + channel_sample[0].guild.name + '\n' \
                '\t Users: ' + users_info)
    
    await post_to_mod_channel(ev, guild_id, channel_sample, users_info, tier, persistance)


    ######################################################
    ##   ACTIONS; TIER actions for severity detection
    ######################################################

    data = await tier_actions_begin(ev, channel_sample, spam_info)
    if data: 
        await asyncio.sleep(60)
        await tier_actions_end(ev, channel_sample, spam_info, data)

    # Reset sample
    try: message_sample.reset_info(*location)
    except: pass
