import discord
import arrow
from sigma.core.permission import check_man_msg
from sigma.core.utils import user_avatar


async def warn(cmd, message, args):

    if not check_man_msg(message.author, message.channel):
        out_content = discord.Embed(color=0xDB0000, title=':no_entry: Users With Kick Permissions Only.')
        await message.channel.send(None, embed=out_content)
        return

    if not message.mentions:
        response = discord.Embed(title='❗ No user targeted.', color=0xDB0000)
        await message.channel.send(embed=response)
        return
    
    if not args:
        await message.channel.send(cmd.help()); 
        return
    
    target = message.mentions[0]
    if target.id == message.author.id:
        response = discord.Embed(title='⛔ You can\'t warn yourself.', color=0xDB0000)
        await message.channel.send(embed=response)
        return

    warning_text = ' '.join(args).replace(target.mention, '')[1:]
    warn_action(cmd, message.guild, message.channel, target, message.author, warning_text)

    out_content_local = discord.Embed(color=0xFF9900, title=f'⚠ {target.name} has been warned.')
    await message.channel.send(None, embed=out_content_local)



async def warn_action(cmd, guild, channel, target, author, warning_text):
    if not warning_text or warning_text == '':
        warning_text = 'No Reason Given'
    
    try: warned_users = cmd.db.get_settings(str(guild.id), 'WarnedUsers')
    except KeyError:
        cmd.db.set_settings(str(guild.id), 'WarnedUsers', {})
        warned_users = {}

    target_id = str(target.id)
    if target_id in warned_users:
        if warned_users[target_id]['Warns'] >= 2:
            out_content_local = discord.Embed(color=0xFF4400, title=f'⚠ {target.name} had 3 warnings.')
            await channel.send(None, embed=out_content_local)
            await target.kick(reason=f'Kicked by {author.name}#{author.discriminator}.\n Has 3 or more warnings')

        # \NOTE: The rest will not happen if the bot has failed to kick the user (user is admin, server owner, etc)
        try:
            warn_data = {
                'UserID': str(warned_users[target_id]['UserID']),
                'Warns': warned_users[target_id]['Warns'] + 1,
                'Reasons': warned_users[target_id]['Reasons'] + [warning_text],
                'Timestamp': warned_users[target_id]['Timestamp'] + [str(arrow.utcnow().timestamp)]
            }
        except:
            warn_data = {
                'UserID': str(warned_users[target_id]['UserID']),
                'Warns': warned_users[target_id]['Warns'] + 1,
                'Reasons': warned_users[target_id]['Reasons'] + [warning_text],
                'Timestamp': [str(warned_users[target_id]['Timestamp'])] + [str(arrow.utcnow().timestamp)]
            }
    else:
        warn_data = {
            'UserID': str(target.id),
            'Warns': 1,
            'Reasons': [warning_text],
            'Timestamp': [str(arrow.utcnow().timestamp)]
        }
    
    warned_users.update({ target_id: warn_data })
    cmd.db.set_settings(str(guild.id), 'WarnedUsers', warned_users)

    out_content_to_user = discord.Embed(color=0xFF9900)
    out_content_to_user.add_field(name=f'⚠ Warning on {guild.name}', value=f'Reason:\n```\n{warning_text}\n```')
    
    try: await target.send(None, embed=out_content_to_user)
    except: pass    
    
    # Logging Part
    try:
        mod_notifications_enabled = cmd.db.get_settings(guild.id, 'ModeratorNotifications')
        if not mod_notifications_enabled: raise Exception
                    
        modchannel_id = cmd.db.get_settings(guild.id, 'ModeratorChannel')
        modchannel    = discord.utils.find(lambda c: c.id == modchannel_id, guild.channels)
    except:
        cmd.log.info('[WARNS] No moderator notification sent because server named ' + guild.name + \
                    ' does not have a moderator channel set up')
    else:
        response = discord.Embed(color=0xFF9900, timestamp=arrow.utcnow().datetime)
        response.set_author(name=f'A User Has Been Warned', icon_url=user_avatar(target))
        response.add_field(name='⚠ Warned User', value=f'{target.mention}\n{target.name}#{target.discriminator}', inline=True)
        response.add_field(name='🛡 Responsible', value=f'{author.mention}\n{author.name}#{author.discriminator}', inline=True)
            
        if warning_text:
            response.add_field(name='📄 Reason', value=f"```\n{warning_text}\n```", inline=False)
            
        response.set_footer(text=f'UserID: {target.id}')
        await modchannel.send(embed=response)