import random
import discord

async def coinflip(cmd, message, args):
    
    cmd.db.add_stats('CoinFlipCount')
    result = random.choice(['heads', 'tails'])
    urls = {
        'heads': 'http://i.imgur.com/KpiOD0g.png',
        'tails': 'http://i.imgur.com/JAPYEsl.png'
    }

    if not args:
        embed = discord.Embed(color=0x1abc9c)
        embed.set_image(url=urls[result])
        await message.channel.send(None, embed=embed)

    choice = args[0]
    valid_choice = choice.lower().startswith('t') or choice.lower().startswith('h')
        
    if not valid_choice:
        embed = discord.Embed(color=0x1abc9c)
        embed.set_footer(text='If you\'re going to guess, guess with Heads or Tails.')
        await message.channel.send(None, embed=embed)
        return

    if choice.lower().startswith('t'):
        choice = 'tails'
    else:
        choice = 'heads'
    
    if result == choice.lower():
        out = ':ballot_box_with_check: Nice guess!'
    else:
        out = ':regional_indicator_x: Better luck next time!'
        
    embed = discord.Embed(color=0x1abc9c, title=out)
    embed.set_image(url=urls[result])
    await message.channel.send(None, embed=embed)
