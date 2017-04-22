import discord
from sigma.core.permission import check_man_chan
from sigma.core.permission import check_man_msg

async def ignorechannel(cmd, message, args):
    if check_man_msg(message.author, message.channel) and check_man_chan(message.author, message.channel):
        target = None

        if not args:
            await cmd.bot.send_message(message.channel, cmd.help())
            return

        qry = ' '.join(args)
        if qry.startswith('<#'): search_id = qry.replace('<#', '').replace('>', '')
        else:                    search_id = args[0]

        for chan in message.server.channels:
            if chan.id == search_id:
                target = chan
                break

        if not target:
            embed = discord.Embed(color=0x696969, title=':notebook: No channel like that was found on this server.')
        else:
            if target == message.author:
                embed = discord.Embed(title=':warning: You Can\'t Blacklist Yourself', color=0xFF9900)
                await cmd.bot.send_message(message.channel, None, embed=embed)
                return

            black = cmd.db.get_settings(message.server.id, 'BlacklistedChannels')
            if not black:
                black = []

            if target.id in black:
                black.remove(target.id)
                embed = discord.Embed(title=':unlock: ' + target.name + ' has been un-blacklisted.', color=0xFF9900)
            else:
                black.append(target.id)
                embed = discord.Embed(title=':lock: ' + target.name + ' has been blacklisted.', color=0xFF9900)

            cmd.db.set_settings(message.server.id, 'BlacklistedChannels', black)
    else:
        embed = discord.Embed(type='rich', color=0xDB0000, title=':no_entry: Insufficient Permissions. Insufficient Permissions. Requires Manage Messages and Manage Channel Permissions(s).')

    await cmd.bot.send_message(message.channel, None, embed=embed)
