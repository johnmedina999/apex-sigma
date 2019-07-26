import giphypop
import discord
from config import GiphyAPIKey

async def giphy(cmd, message, args):
    
    cmd.db.add_stats('NekoCount')

    search = ''.join(args).strip()
    if search == '': await message.channel.send(cmd.help()); return

    if GiphyAPIKey == '':
        embed = discord.Embed(color=0xDB0000)
        embed.add_field(name='API key GiphyAPIKey not found.', value='Please ask the bot owner to add it.')
        await message.channel.send(None, embed=embed)
        return

    giphy = giphypop.Giphy(api_key=GiphyAPIKey)
    result = giphy.screensaver(search)

    await message.channel.send(result.url)
