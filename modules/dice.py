#!/usr/bin/env python
"""
dice.py - Dice roll Module
"""

from random import randint

_dice = [u"\u2680", u"\u2680", u"\u2680", u"\u2680", u"\u2680", u"\u2680"] 

def diceroll(bot, input):
    """Lucky roll"""
    if not input.group(2):
        rand_upper = 6
    else:
        try:
            rand_upper = int(input.group(2).strip())
        except:
            rand_upper = 6

    bot.reply("Rolling... and: [-" + str(randint(1,rand_upper)) + "-]")
diceroll.commands = ['dice', 'roll']
