import discord

async def ranking(cmd, message, args):

    query = {
        'ServerID': message.server.id
    }

    embed = discord.Embed(title=':gem: ' + message.server.name + ' Ranking Top 10', color=0x0099FF)
    number_grabber = cmd.db.find('PointSystem', query).sort('Points', -1)

    rankingData = {'numbers': '', 'users': '', 'points': ''}
    count = 0

    for result in number_grabber:
        number = user = points = ''
        try:
            count += 1
            if count > 10: break

            number = str(count) + "\n"
            user = message.server.get_member(result['UserID']).name + "\n"
            points = str(result['Points']) + "\n"
        except: pass

        rankingData['numbers'] += number
        rankingData['users'] += user
        rankingData['points'] += points

    embed.add_field(name='#', value=rankingData['numbers'])
    embed.add_field(name='Users', value=rankingData['users'])
    embed.add_field(name='Points', value=rankingData['points'])

    await cmd.bot.send_message(message.channel, None, embed=embed)
