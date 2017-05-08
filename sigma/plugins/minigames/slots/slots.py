import random
from .slot_core import spin_slots


async def slots(cmd, message, args):
    cost = 8
    emoji = 2

    if args:
        try: 
            #cost = abs(int(args[0]))
            emoji = min(20, max(2, int(args[0])))
        except: pass

    cost = pow(emoji, 4)
    symbols = [':sunny:', ':crescent_moon:', ':eggplant:', ':gun:', ':diamond_shape_with_a_dot_inside:', ':bell:',
               ':maple_leaf:', ':musical_note:', ':gem:', ':fleur_de_lis:', ':trident:', ':knife:', ':fire:',
               ':clown:', ':radioactive:', ':green_heart:', ':telephone:', ':hamburger:', ':banana:',
               ':tumbler_glass:']

    while len(symbols) > emoji:
        choose = random.randint(0, len(symbols) - 1)
        del symbols[choose]

    await spin_slots(cmd, message, cost, symbols)
