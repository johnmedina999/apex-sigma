import asyncio
import discord
import arrow
import copy

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

PERSISTANCE = 0
TIER        = 1
MUTED       = 2

def add_to_spam_info(ev, guild_id, channel_id):
    global spam_info                # Contains how persistant spam is on a server (persistance, tier)

    try:
        if spam_info[guild_id][channel_id][PERSISTANCE] == 2:
            spam_info[guild_id][channel_id][PERSISTANCE] = 0
            spam_info[guild_id][channel_id][TIER] += 1
        else:
            spam_info[guild_id][channel_id][PERSISTANCE] += 1
    except:
        try: spam_info[guild_id][channel_id] = [0, 1, False]
        except:
            try: 
                spam_info[guild_id] = {}
                spam_info[guild_id][channel_id] = [0, 1, False]
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

    for guild_id, guild_sample in copy.copy(message_sample).items():
        for channel_id, channel_sample in copy.copy(guild_sample).items():
            
            ######################################################
            ##   Prcessing
            ######################################################

            try: # Skip processing if the channel is muted due to spamming; It's being processed in another task
                if spam_info[guild_id][channel_id][MUTED]: continue
            except: pass

            # If number of messages don't exceed spam threshold, then reset persistance
            if len(channel_sample) < ev.db.get_settings(guild_id, 'SpamThreshold'): 
                try: del spam_info[guild_id][channel_id]
                except: pass
                continue

            add_to_spam_info(ev, guild_id, channel_id)
            
            # 100 msgs is max it can delete at once
            if len(channel_sample) > 75 and spam_info[guild_id][channel_id][TIER] < 3:
                spam_info[guild_id][channel_id][TIER] = 3      # Auto escalation as panic response

            persistance = spam_info[guild_id][channel_id][PERSISTANCE]
            tier = spam_info[guild_id][channel_id][TIER]


            ######################################################
            ##   Notifications
            ######################################################

            users_info = ', '.join([ message.author.name for message in channel_sample ])
            ev.log.info('[SPAM MONITOR] TIER ' + str(tier) + ' - Channel Detected: ' + channel_sample[0].channel.name + ' in ' + channel_sample[0].guild.name + '\n' \
                        '\t Users: ' + users_info)

            try:
                mod_notifications_enabled = ev.db.get_settings(guild_id, 'ModeratorNotifications')
                if not mod_notifications_enabled: raise Exception
                    
                modchannel_id = ev.db.get_settings(guild_id, 'ModeratorChannel')
                modchannel    = discord.utils.find(lambda c: c.id == modchannel_id, channel_sample[0].guild.channels)
            except:
                ev.log.info('[SPAM MONITOR] No moderator notification sent because server named ' + channel_sample[0].guild.name + \
                            ' does not have a moderator channel set up')
            else:
                actions = ''
                if tier >= 1: actions += 'Deleted Messages'
                if tier >= 2: actions += ', Warned users'
                if tier >= 3: actions += ', Muted Channel'
                if tier >= 4: actions += ', Disabled invites'
                if tier >= 5: actions = 'PANIC!!! IT\'S THE END OF THE WORLD AS WE KNOW IT!!! :bat: :skull:'
    
                embed = discord.Embed(title='TIER ' + str(tier) + ' SPAM EVENT DETECTED', color=0xDB0000)
                embed.add_field(name='Channel: ', value=channel_sample[0].channel.name)
                embed.add_field(name='Action Taken: ', value=actions)
                embed.add_field(name='Users: ', value=users_info)

                await modchannel.send(None, embed=embed)

                if tier == 2 and persistance == 2:
                    pass #await modchannel.send(":bat: @here AHHHH!!! Where are the mods??? Help me!!!")


            ######################################################
            ##   ACTIONS; TIER actions for severity detection
            ######################################################

            if tier >= 1: 
                try: await channel_sample[0].channel.delete_messages(channel_sample)
                except discord.errors.NotFound: pass
            if tier >= 2: 
                if persistance == 1:
                    embed = discord.Embed(title=':bat: Stop Spamming!!! :bat:', color=0xDBD000)
                    await channel_sample[0].channel.send(None, embed=embed)
            if tier >= 3:

                '''
                everyone_role = discord.utils.find(lambda r: r.name == '@everyone', channel_sample[0].guild.roles)
                permissions = channel_sample[0].channel.overwrites_for(everyone_role)
                
                permissions.send_messages = False
                await channel_sample[0].channel.set_permissions(everyone_role, overwrite=permissions)
                spam_info[guild_id][channel_id][MUTED] = True

                await asyncio.sleep(60)
                
                permissions.send_messages = True
                await channel_sample[0].channel.set_permissions(everyone_role, overwrite=permissions)
                spam_info[guild_id][channel_id][MUTED] = False
                '''

                spam_info[guild_id][channel_id][MUTED] = True
                roles_changed  = []
                added_overides = []

                for role in channel_sample[0].guild.roles:
                    try:
                        # Check role permissions
                        general_permission = 0b01111100000000000000000010111111
                        if role.permissions.value > general_permission: continue
                        if role.permissions.send_messages == False: continue
                    
                        # Check channel role overides
                        permissions = channel_sample[0].channel.overwrites_for(role)
                        if permissions.send_messages == False: continue
                    
                        if permissions.is_empty(): added_overides.append(role)
                        else: roles_changed.append(role)

                        # Apply channel specific role mute
                        permissions.send_messages = False
                        await channel_sample[0].channel.set_permissions(role, overwrite=permissions)
                        
                    except:
                        ev.log.info('[SPAM MONITOR] Unable to disable @' + role.name + ' send messages permission for channel ' + channel_sample[0].channel.name + ' in ' + channel_sample[0].guild.name)
                
                await asyncio.sleep(60)
                
                for role in roles_changed:
                    permissions = channel_sample[0].channel.overwrites_for(role)
                    permissions.send_messages = True
                    await channel_sample[0].channel.set_permissions(role, overwrite=permissions)

                for role in added_overides:
                    await channel_sample[0].channel.set_permissions(role, overwrite=None)

                spam_info[guild_id][channel_id][MUTED] = False
                    
                # TODO: Send warns to all people that spammed
                #       warn(cmd, message, args)
            if tier >= 4: 
                # TODO: Revoke invite links
                #  ev.db.set_settings(guild_id, 'BlockInvites', True)
                #  embed = discord.Embed(color=0x66CC66, title=':white_check_mark: Invite Blocking Has Been Enabled')
                #  await admin_channel.send(None, embed=embed)  # send alert to admin channel
                pass

    # Reset sample, update time
    message_sample = {}
    prev_time = arrow.utcnow().timestamp
