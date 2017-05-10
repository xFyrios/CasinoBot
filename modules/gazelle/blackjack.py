#!/usr/bin/env python

import casino

def hit(phenny, input):
    if casino.game:
        args = casino.check_args(phenny, input.group(0))
        if not args:
            casino.game.hit(input.uid)

        if args[0].isdigit():
            handid = int(args[0])
            casino.game.hit(input.uid, handid)
        else:
            phenny.write(('NOTICE', input.nick + " Specify the hand using a digit. Ex. !hit 1"))
hit.commands = ['hit', 'Hit', 'h']
hit.priority = 'high'

def stand(phenny, input):
    if casino.game:
        args = casino.check_args(phenny, input.group(0))
        if not args:
            casino.game.stand(input.uid)

        if args[0].isdigit():
            handid = int(args[0])
            casino.game.stand(input.uid, handid)
        else:
            phenny.write(('NOTICE', input.nick + " Specify the hand using a digit. Ex. !stand 1"))
stand.commands = ['stand', 'Stand', 'stay', 'Stay', 's']

def split(phenny, input):
    if casino.game:
        args = casino.check_args(phenny, input.group(0))
        if not args:
            casino.game.split(input.uid)

        if args[0].isdigit():
            handid = int(args[0])
            casino.game.split(input.uid, handid)
        else:
            phenny.write(('NOTICE', input.nick + " Specify the hand using a digit. Ex. !split 1"))
split.commands = ['split', 'Split', 'sp']

def surrender(phenny, input):
    if casino.game:
        casino.game.surrender(input.uid)
surrender.commands = ['surrender', 'Surrender']

def doubledown(phenny, input):
    if casino.game:
        args = casino.check_args(phenny, input.group(0))
        if not args:
            casino.game.doubledown(input.uid)

        if args[0].isdigit():
            handid = int(args[0])
            casino.game.doubledown(input.uid, handid)
        else:
            phenny.write(('NOTICE', input.nick + " Specify the hand using a digit. Ex. !doubledown 1"))
doubledown.commands = ['doubledown','DoubleDown','double','Double']

def hand(phenny, input):
    if casino.game:
        casino.game.hand(input.uid)
hand.commands = ['hand']

if __name__ == '__main__':
    print(__doc__)

