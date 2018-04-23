#!/usr/bin/env python

import casino

def hit(phenny, input):
    if casino.game and casino.game.game_type == 'blackjack':
        casino.game.hit(input.uid)
hit.commands = ['hit', 'Hit', 'h']
hit.priority = 'high'

def stand(phenny, input):
    if casino.game and casino.game.game_type == 'blackjack':
        casino.game.stand(input.uid)
stand.commands = ['stand', 'Stand', 'stay', 'Stay', 's']

def surrender(phenny, input):
    if casino.game and casino.game.game_type == 'blackjack':
        casino.game.surrender(input.uid)
surrender.commands = ['surrender', 'Surrender']

def doubledown(phenny, input):
    if casino.game and casino.game.game_type == 'blackjack':
        casino.game.doubledown(input.uid)
doubledown.commands = ['doubledown','DoubleDown','double','Double']

def split(phenny, input):
    if casino.game and casino.game.game_type == 'blackjack':
        casino.game.split(input.uid)
split.commands = ['split', 'Split', 'sp']

def hand(phenny, input):
    if casino.game and casino.game.game_type == 'blackjack':
        casino.game.hand(input.uid)
hand.commands = ['hand']

if __name__ == '__main__':
    print(__doc__)

