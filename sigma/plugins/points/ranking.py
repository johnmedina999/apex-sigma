import discord

async def ranking(cmd, message, args):

    query = {
        'ServerID': message.server.id
    }

    embed = discord.Embed(title=':gem: ' + message.server.name + ' Ranking Top 10', color=0x0099FF)
    number_grabber = cmd.db.find('PointSystem', query).sort('Points', -1)

    points = ''
    users = ''
    numbers = ''
    count = 0

    for result in number_grabber:
        try:
            count += 1
            if count > 10: break

            numbers += str(count) + "\n"
            users += message.server.get_member(result['UserID']).name + "\n"
            points += str(result['Points']) + "\n"
        except: pass

    embed.add_field(name='#', value=numbers)
    embed.add_field(name='Users', value=users)
    embed.add_field(name='Points', value=points)

    await cmd.bot.send_message(message.channel, None, embed=embed)
