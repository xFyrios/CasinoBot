#!/usr/bin/env python

import casino

def hit(phenny, input):
    if casino.game:
        casino.game.hit(input.uid)
hit.commands = ['hit', 'Hit', 'h']
hit.priority = 'high'

def stand(phenny, input):
    if casino.game:
        casino.game.stand(input.uid)
stand.commands = ['stand', 'Stand', 'stay', 'Stay', 's']

def surrender(phenny, input):
    if casino.game:
        casino.game.surrender(input.uid)
surrender.commands = ['surrender', 'Surrender']

def doubledown(phenny, input):
    if casino.game:
        casino.game.doubledown(input.uid)
doubledown.commands = ['doubledown','double']

def hand(phenny, input):
    if casino.game:
        casino.game.hand(input.uid)
hand.commands = ['hand']

if __name__ == '__main__':
    print(__doc__)

