import discord
from datetime import datetime, timedelta
from pytz import timezone, UnknownTimeZoneError, utc
from geopy import geocoders
from tzwhere import tzwhere


async def time(cmd, message, args):

    if not args:
        await cmd.bot.send_message(message.channel, cmd.help())
        return

    if len(args) < 1:
        await cmd.bot.send_message(message.channel, cmd.help())
        return

    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    UTC = datetime.utcnow()

    if is_int(args[0]):
        # add the '+' if no sign is present
        if args[0].find('+') == -1 and args[0].find('-') == -1:
            args[0] = '+' + args[0]

        UTC_offset_to = int(args[0])
        if UTC_offset_to >= 24 or UTC_offset_to <= -24:
            embed = discord.Embed(title=':exclamation: Invalid UTC offset', color=0x993333)
            await cmd.bot.send_message(message.channel, None, embed=embed)
            return

        time = UTC + timedelta(hours=UTC_offset_to)

        embed = discord.Embed(title=':clock10: Converted time', color=0x0099FF)
        embed.add_field(name=f'UTC' + args[0], value=time.strftime(TIME_FORMAT), inline=False)
        await cmd.bot.send_message(message.channel, None, embed=embed)
        return

    else:
        try:
            # Specify it is of UTC timezone and convert
            UTC = UTC.replace(tzinfo=utc)
            time = UTC.astimezone(timezone(args[0]))

            embed = discord.Embed(title=':clock10: Converted time', color=0x0099FF)
            embed.add_field(name=args[0], value=time.strftime(TIME_FORMAT), inline=False)
            await cmd.bot.send_message(message.channel, None, embed=embed)
            return

        # Try to resolve it as a location
        except UnknownTimeZoneError:
            try:
                g = geocoders.GoogleV3()
                place_timezone = g.timezone(g.geocode(args[0]).point)
                time = UTC.astimezone(timezone(str(place_timezone)))

                embed = discord.Embed(title=':clock10: Converted time', color=0x0099FF)
                embed.add_field(name=str(place_timezone), value=time.strftime(TIME_FORMAT), inline=False)
                await cmd.bot.send_message(message.channel, None, embed=embed)
                return

            except AttributeError:
                embed = discord.Embed(title=':question: Unknown Timezone/Location', color=0x993333)
                await cmd.bot.send_message(message.channel, None, embed=embed)
                return

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False