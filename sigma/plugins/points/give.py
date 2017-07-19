import discord


async def give(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help())
        return
    
    if not message.mentions:
        await message.channel.send(cmd.help())
        return
    
    if len(args) < 2:
        await message.channel.send(cmd.help())
        return
    
    target_user = message.mentions[0]
    if target_user.bot: 
        await message.channel.send("The bot refused to take your points!")
        return

    if target_user == message.author: 
        await message.channel.send("...and nothing happened")
        return

    try: amount = int(args[1])
    except: await message.channel.send(f"I'm sorry, how many points is {args[0]} worth?"); return

    if amount < 0:
        await message.channel.send("You tried giving negative points, but failed :("); 
        return

    if amount == 0:
        await message.channel.send("You gave 0 points, but your efforts go unnoticed."); 
        return

    curr_points = cmd.db.get_points(message.author)['Current']
    if amount > curr_points:
        out_content = discord.Embed(type='rich', color=0xDB0000, title=':no_entry: You Do Not Have Enough Points.')
        await message.channel.send(None, embed=out_content)
        return
    
    cmd.db.take_points(message.guild, message.author, amount)
    cmd.db.add_points(message.guild, target_user, amount)
    
    out_content = discord.Embed(type='rich', color=0x66CC66, title=':white_check_mark: Points Transferred.')
    await message.channel.send(None, embed=out_content)
