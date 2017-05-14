#!/usr/bin/env python

import casino

def ante(phenny, input):
    if casino.game and casino.game.game_type == 'poker':
        casino.game.ante(input.uid, input.nick)
ante.commands = ['ante']

def raise_bet(phenny, input):
    if casino.game and casino.game.game_type == 'poker':
        args = input.group(0).split()
        cmd = args[0][1:]
        args.pop(0)
        casino.game.raise_bet(input.uid, args[0])
raise_bet.commands = ['raise']

def check(phenny, input):
    if casino.game and casino.game.game_type == 'poker':
        casino.game.check(input.uid, False)
check.commands = ['check']

def call(phenny, input):
    if casino.game and casino.game.game_type == 'poker':
        casino.game.call(input.uid)
call.commands = ['call']

def fold(phenny, input):
    if casino.game and casino.game.game_type == 'poker':
        casino.game.fold(input.uid, False)
fold.commands = ['fold']

def discard(phenny, input):
    if casino.game and casino.game.game_type == 'poker':
        args = input.group(0).split()
        cmd = args[0][1:]
        args.pop(0)
        casino.game.discard(input.uid, args)
discard.commands = ['discard']

def pass_discard(phenny, input):
    if casino.game and casino.game.game_type == 'poker':
        casino.game.pass_discard(input.uid, False)
pass_discard.commands = ['pass']

if __name__ == '__main__':
    print(__doc__)

