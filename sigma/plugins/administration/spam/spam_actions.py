import asyncio
import discord

from .spam_data import SpamInfo
from ...moderation.warns.warn import warn_action


async def post_to_mod_channel(ev, guild_id, channel_sample, users_info, tier, persistance):
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
        if tier >= 4: actions += ', Redirected autorole'
        if tier >= 5: actions = 'PANIC!!! IT\'S THE END OF THE WORLD AS WE KNOW IT!!! :bat: :skull:'
    
        embed = discord.Embed(title='TIER ' + str(tier) + ' SPAM EVENT DETECTED', color=0xDB0000)
        embed.add_field(name='Channel: ', value=channel_sample[0].channel.name)
        embed.add_field(name='Action Taken: ', value=actions)
        embed.add_field(name='Users: ', value=users_info)

        await modchannel.send(None, embed=embed)

        if tier == 2 and persistance == 2:
            pass #await modchannel.send(":bat: @here AHHHH!!! Where are the mods??? Help me!!!")


async def tier_actions_begin(ev, channel_sample, spam_info):
    guild       = channel_sample[0].guild
    channel     = channel_sample[0].channel
    tier        = spam_info.get_spam_tier(ev, guild.id, channel.id)
    persistance = spam_info.get_persistance(ev, guild.id, channel.id)
    data        = {}

    if tier >= 1: 
        try: await channel.delete_messages(channel_sample)
        except discord.errors.NotFound: pass

    if tier >= 2: 
        if persistance == 1:
            embed = discord.Embed(title=':bat: Stop Spamming!!! :bat:', color=0xDBD000)
            await channel.send(None, embed=embed)

    if tier >= 3:

        # TODO: Fix bug: https://i.imgur.com/haIkpjZ.png
        spam_info.set_muted_status(ev, guild.id, channel.id, status=True)
        
        data['roles_changed']  = []
        data['added_overides'] = []

        for role in guild.roles:
            try:
                # Check role permissions
                general_permission = 0b01111100000000000000000010111111
                if role.permissions.value > general_permission: continue
                if role.permissions.send_messages == False: continue
            
                # Check channel role overides
                permissions = channel.overwrites_for(role)
                if permissions.send_messages == False: continue
            
                if permissions.is_empty(): data['added_overides'].append(role)
                else: data['roles_changed'].append(role)

                # Apply channel specific role mute
                permissions.send_messages = False
                await channel.set_permissions(role, overwrite=permissions)
                
            except:
                ev.log.info('[SPAM MONITOR] Unable to disable @' + role.name + ' send messages permission for channel ' + channel.name + ' in ' + guild.name)
                    
        # Send warns to all people that spammed
        users_warned = set()
        for message in channel_sample:
            if not message.author.id in users_warned:
                try: await warn_action(ev, guild, channel, message.author, ev.bot.user, 'Stop spamming')
                except: ev.log.info('[SPAM MONITOR] Unable to warn ' + message.author.name + ' in channel ' + channel.name + ' in guild ' + guild.name)
                users_warned.add(message.author.id)

    if tier >= 4:
        try: autorole = ev.db.get_settings(guild.id, 'AutoRole')
        except KeyError: data['prev_autorole'] = None
        else:            data['prev_autorole'] = autorole

        # Create a channel if it doesn't exist meant to contain a sudden influx of invites
        # Channel will allow anyone with the "restricted" role to see and talk
        # When TIER is descalates, keep the channel
        restricted_role = discord.utils.find(lambda r: r.name == 'restricted', guild.roles)
        if not restricted_role:
            restricted_role = await guild.create_role(name='restricted')

        restricted_channel = discord.utils.find(lambda c: c.name == 'restricted', guild.channels)
        if not restricted_channel:
            restricted_channel_overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                restricted_role:    discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            await guild.create_text_channel(name='restricted', overwrites=restricted_channel_overwrites)
    
        # Set autorole to give the "restricted" role
        ev.db.set_settings(guild.id, 'AutoRole', restricted_role.id)

    return data


async def tier_actions_end(ev, channel_sample, spam_info, data):
    guild       = channel_sample[0].guild
    channel     = channel_sample[0].channel
    tier        = spam_info.get_spam_tier(ev, guild.id, channel.id)
    persistance = spam_info.get_persistance(ev, guild.id, channel.id)
    
    if tier >= 1: pass

    if tier >= 2: pass

    if tier >= 3:
        # Revert role permissions
        for role in data['roles_changed']:
            permissions = channel_sample[0].channel.overwrites_for(role)
            permissions.send_messages = True
            await channel_sample[0].channel.set_permissions(role, overwrite=permissions)

        for role in data['added_overides']:
            await channel_sample[0].channel.set_permissions(role, overwrite=None)

        spam_info.set_muted_status(ev, guild.id, channel.id, False)

    if tier >= 4:
        # Revert autorole
        ev.db.set_settings(guild.id, 'AutoRole', data['prev_autorole'])
