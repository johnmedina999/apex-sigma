from sigma.core.permission import check_man_msg
from sigma.core.permission import check_man_roles
from sigma.core.permission import check_write
import discord


async def blind(cmd, message, args):
    channel = message.channel
    server = message.server

    if len(args) < 2 or not message.mentions:
        await cmd.bot.send_message(message.channel, cmd.help())
        return

    target = message.mentions[0]
    reason = ' '.join(args).replace(target.mention, '')[1:]

    if target == cmd.bot.user:
        embed = discord.Embed(title=':warning: You Can\'t Blind Me', color=0xFF9900)
        await cmd.bot.send_message(message.channel, None, embed=embed)
        return

    if target == message.author:
        embed = discord.Embed(title=':warning: You Can\'t Blind Yourself', color=0xFF9900)
        await cmd.bot.send_message(message.channel, None, embed=embed)
        return

    overwrite = discord.PermissionOverwrite()
    overwrite.read_messages = False

    if check_man_msg(message.author, channel) and check_man_roles(message.author, channel):
        for chan in server.channels:
            if not chan.is_default:
                if str(chan.type).lower() == 'text':
                    if check_write(target, chan):
                        await cmd.bot.edit_channel_permissions(chan, target, overwrite)

        out_content_to_user = discord.Embed(color=0x993300)
        out_content_to_user.add_field(name=':eye_in_speech_bubble: You have been blinded!', value=('Reason: ' + reason))
        await cmd.bot.send_message(target, None, embed=out_content_to_user)

        embed = discord.Embed(color=0x66CC66, title=':white_check_mark: ' + target.name + ' Was Blinded!')
        await cmd.bot.send_message(message.channel, None, embed=embed)
    else:
        out_content = discord.Embed(color=0xDB0000,title=':no_entry: Insufficient Permissions. Users with Ban permissions only.')
        await cmd.bot.send_message(message.channel, None, embed=out_content)
