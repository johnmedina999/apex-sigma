import random
from config import Prefix


async def reward(ev, message, args):
    if message.author.bot: return
    if message.guild:
        if message.content.startswith(Prefix): return
        if ev.cooldown.on_cooldown(ev, message): return
                                
        points = random.randint(3, 15)
        ev.db.add_points(message.guild, message.author, points)
        ev.cooldown.set_cooldown(ev, message, 60)