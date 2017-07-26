import giphypop
from config import GiphyAPIKey

async def giphy(cmd, message, args):
    
    cmd.db.add_stats('NekoCount')

    search = ''.join(args).strip()
    if search == '': await message.channel.send(cmd.help()); return

    giphy = giphypop.Giphy(api_key=GiphyAPIKey)
    result = giphy.screensaver(search)

    await message.channel.send(result.url)
