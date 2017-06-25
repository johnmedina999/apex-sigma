'''import discord
from sigma.core.permission import check_admin
from sigma.core.permission import check_kick
from sigma.core.permission import check_man_msg


async def ignoreuser(cmd, message, args):
    if check_man_msg(message.author, message.channel) and check_kick(message.author, message.channel):
        target = None

        if not args:
            await cmd.bot.send_message(message.channel, cmd.help())
            return

        if message.mentions:
            target = message.mentions[0]
        else:
            for user in message.server.members:
                if user.id == args[0]:
                    target = user
                    break
                elif user.name.lower() == args[0].lower():
                    target = user
                    break

        if not target:
            embed = discord.Embed(color=0x696969, title=':notebook: No channel like that was found on this server.')
        else:
            if check_admin(target, message.channel):
                embed = discord.Embed(title=':warning: You Can\'t Blacklist an admin', color=0xFF9900)
                await cmd.bot.send_message(message.channel, None, embed=embed)
                return

            if target == message.author:
                embed = discord.Embed(title=':warning: You Can\'t Blacklist Yourself', color=0xFF9900)
                await cmd.bot.send_message(message.channel, None, embed=embed)
                return

            if target == cmd.bot.user:
                embed = discord.Embed(title=':warning: You Can\'t Blacklist Me', color=0xFF9900)
                await cmd.bot.send_message(message.channel, None, embed=embed)
                return

            black = cmd.db.get_settings(message.server.id, 'BlacklistedUsers')
            if not black:
                black = []

            if target.id in black:
                black.remove(target.id)
                embed = discord.Embed(title=':unlock: ' + target.name + ' has been un-blacklisted.', color=0xFF9900)
            else:
                black.append(target.id)
                embed = discord.Embed(title=':lock: ' + target.name + ' has been blacklisted.', color=0xFF9900)

            cmd.db.set_settings(message.server.id, 'BlacklistedUsers', black)
    else:
        embed = discord.Embed(type='rich', color=0xDB0000, title=':no_entry: Insufficient Permissions. Requires Manage Messages and Kick Permissions(s).')

    await cmd.bot.send_message(message.channel, None, embed=embed)
'''