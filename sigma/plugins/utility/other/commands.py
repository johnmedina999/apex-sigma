import discord
from config import Prefix


async def commands(cmd, message, args):
    
    if not args:
        embed = discord.Embed(color=0x696969, title='🔍 Please Enter a Module Name.')
        embed.set_footer(text='The module groups can be seen with the ' + Prefix + 'help command.')
        await message.channel.send(None, embed=embed)
        return

    module_group = ' '.join(args).lower()
    command_list = []
    all_commands = cmd.bot.plugin_manager.commands
    
    for command in all_commands:
        if module_group in all_commands[command].plugin.categories:
            command_list.append(f'{Prefix}{command}')
    
    if len(command_list) == 0:
        embed = discord.Embed(color=0x696969, title='🔍 Module Group Not Found!')
        await message.channel.send(None, embed=embed)
        return
    
    embed_to_channel = discord.Embed(color=0x1abc9c)
    embed_to_channel.add_field(name='Sickle\'s commands in ' + module_group.title(), value='```yaml\n' + ', '.join(command_list) + '\n```')
    await message.channel.send(None, embed=embed_to_channel)
