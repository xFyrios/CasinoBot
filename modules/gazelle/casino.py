#!/usr/bin/env python

import blackjack, poker, cards as c, player as p
from collections import OrderedDict
import time
from threading import Timer
from random import randint

# The list of bots to never join in games
bots = ['CasinoBot', 'Vertigo', 'Antilopinae']

game = False # Holds the game object
in_play = False  # Used to test if the game is in play
starting = False # Used to prevent 2 games in the rare instance 2 people try to start one at once
leaving = []  # Used to hold player ids of players who ran !left but we are waiting on confirmation from
gold = 0

arguments = {'start': 1, 'enter': 0, 'leave': 0, 'buy': 1, 'sell': 1, 'bet': 1, 'allin': 0, 'bets': 0, 'hand': 0, 'player': 0, 'players': 0}
help = OrderedDict([('start', "To start a game use the command '!start gamename'. Games you can start include blackjack, poker (5-card), or 7poker (7-card). "
                              " For poker you can also optionally set the stakes. Ex. '!poker stakes' This can be 'high' or 'low', default is 'normal'. For more info see the wiki."),
                    ('enter', "To enter a game that is currently running, use the command '!enter'."),
                    ('leave', "To leave a game that is running, use the command '!leave'. Note that if you have"
                              "placed any bets, your bet will be forfeit."),
                    ('buy', "To buy into a game, use the command '!buy amount'. Ex. !buy 1000. "
                            "This will remove 1000 gold from you on-site and add it to your betting pool."),
                    ('sell', "To cash out use the command '!sell amount'. Ex. !sell 1000. This will remove 1000 "
                             "gold from your betting pool and add it back to your account on-site. Use '!sell all' to cash out fully."),
                    ('bet', "To place a bet use the command '!bet amount'. Ex. !bet 100. You can only "
                            "bet during betting rounds."),
                    ('allin', "To bet all of your gold use the command '!allin'. You can only bet during betting rounds."),
                    ('bets', "To view all current bets around the table, use the command '!bets'."),
                    ('hand', "To view your hand, use the command '!hand'."),
                    ('credits', "To view how many credits you have bought, use the command '!credits'."),
                    ('players', "To view all players in-game, use the command !players. Optionally, you can use"
                                "'!players all' to view all players in the room. If no game is running it will"
                                "default to all."),
                    ('player', "To view a players stats use the command '!player username' or '!player userid'. "
                               "Ex. !player Ted")])
temp_cmds = [] # Holds commands added to help from another module


# Add/remove users from the players list on join/part
def casino_join(phenny, input):
    join_casino(input)
casino_join.event = 'JOIN'
casino_join.rule = r'.*'
casino_join.priority = 'high'

def casino_part(phenny, input):
    if input.uid in p.players.keys():
        if in_play and input.uid in p.in_game:
            p.remove_from_game(input.uid)
            if hasattr(game, 'started') and game.started:
                phenny.say("%s forfeit their bet and left the game early." % p.players[input.uid].name)
            else:
                phenny.say("%s left the game." % p.players[input.uid].name)
            if len(p.in_game) == 0:
                game.game_over()
        p.remove_player(input.uid)
casino_part.event = 'PART'
casino_part.rule = r'.*'
casino_part.priority = 'high'

# Help commands
def casino_help(phenny, input):
    if not input.group(2):
        phenny.say('Commands I recognize include: ' + ', '.join(help.keys()))
        phenny.say("For more info on a command, type '!casinohelp cmd' where cmd is the name of the command you want help for.")
    else:
        cmd = input.group(2)
        if cmd in help.keys():
            phenny.say(help[cmd])
        else:
            phenny.say('That command does not exist.')
            phenny.say('Commands I recognize include: ' + ', '.join(help.keys()))
casino_help.commands = ['casinohelp']
casino_help.priority = 'low'

# Buy / Sell chips
def buy(phenny, input):
    args = check_args(phenny, input.group(0))
    if not args:
        return

    amount = args[0]
    if amount.isdigit():
        join_casino(input)
        #Ask the site for gold
        success = phenny.callGazelleApi({'uid': input.uid, 'amount': amount, 'action': 'buyGold'})
        if success == False or success['status'] == "error":
            if success['error'] != 'Invalid Form Data' and success['error'] != 'error':
                phenny.write(('NOTICE', input.nick + " " + success['error']))  # NOTICE
            else:
                phenny.write(('NOTICE', input.nick + " An unknown error occurred."))  # NOTICE
            return False
        else:
            p.players[input.uid].add_gold(amount)
            phenny.write(('NOTICE', input.nick + " You bought " + str(amount) + " gold worth of chips."))  # NOTICE
    else:
        phenny.write(('NOTICE', input.nick + " You can only buy in with a positive, non-decimal amount of gold. Ex. !buy 100"))  # NOTICE
buy.commands = ['buy']

def sell(phenny, input):
    args = check_args(phenny, input.group(0))
    if not args:
        return

    # Mod command, make all users sell
    if args[0] == "out":
        if input.mod:
            for uid in p.players.keys():
                if p.players[uid].gold > 0:
                    success = phenny.callGazelleApi({'uid': uid, 'amount': p.players[uid].gold, 'action': 'sellGold'})
                    if success == False or success['status'] == "error":
                        phenny.write(('NOTICE', input.nick + " An unknown error occurred. Could not sell " + p.players[uid].name + "'s gold."))  # NOTICE
                    else:
                        p.players[uid].remove_gold(p.players[uid].gold)
            phenny.say("Forced all users to sell out.")
            donate(phenny, True)
        else:
            phenny.say("You do not have permission to use this command.")

    elif args[0] == "all":
        if input.uid in p.players.keys():
            amount = p.players[input.uid].gold
            success = phenny.callGazelleApi({'uid': input.uid, 'amount': amount, 'action': 'sellGold'})
            if success == False or success['status'] == "error":
                phenny.write(('NOTICE', input.nick + " An unknown error occurred."))  # NOTICE
            else:
                p.players[input.uid].remove_gold(amount)
                phenny.write(('NOTICE', input.nick + " You sold " + str(amount) + " gold worth of chips."))  # NOTICE

    else:
        amount = args[0]
        if amount.isdigit() and int(amount) > 0 and input.uid in p.players.keys():
            if int(amount) > p.players[input.uid].gold:
                amount = p.players[input.uid].gold
            success = phenny.callGazelleApi({'uid': input.uid, 'amount': amount, 'action': 'sellGold'})
            if success == False or success['status'] == "error":
                phenny.write(('NOTICE', input.nick + " An unknown error occurred."))  # NOTICE
            else:
                p.players[input.uid].remove_gold(amount)
                phenny.write(('NOTICE', input.nick + " You sold " + str(amount) + " gold worth of chips."))  # NOTICE
        else:
            phenny.write(('NOTICE', input.nick + " You can only cash out with a positive, non-decimal amount of gold. Ex. !sell 100"))  # NOTICE
sell.commands = ['sell']

# Show all players or show a players stats
def players(phenny, input):
    if len(p.players) > 0:
        if input.group(0) == "all" or not in_play:
            phenny.say(p.list_players())
        elif len(p.in_game) > 0:
             phenny.say(p.list_in_game())
        else:
            phenny.say("An error occurred.")
    else:
        phenny.say("There are currently no players registered.")
players.commands = ['players']
players.priority = 'low'

def player(phenny, input):
    args = check_args(phenny, input.group(0))
    join_casino(input)
    if len(args) == 0:
        uid = input.uid
    elif args[0].isdigit():
        uid = args[0]
    else:
        uid = p.name_to_uid(args[0])
    
    if uid is None or uid not in p.players.keys():
        phenny.say("That user does not exist. Try !players to view all registered players.")
    else:
        phenny.say(str(p.players[uid]))
player.commands = ['player']
player.priority = 'low'

def balance(phenny, input):
    if input.uid in p.players:
        phenny.write(('NOTICE', input.nick + " You have: " + str(p.players[input.uid].gold) + " gold"))  # NOTICE
balance.commands = ['balance', 'credits', 'gold', 'chips']
balance.priority = 'low'

# Start a new game
def start(phenny, input):
    global game, in_play, starting, arguments, help, temp_cmds
    if not starting:
        starting = True
        args = check_args(phenny, input.group(0))
        if not args:
            starting = False
            return

        if in_play:
            phenny.say("A game is already in play! Wait for it to end, then try again.")
        else:
            #NEW BLACKJACK GAME
            if args[0] == "blackjack":
                in_play = True
                join_casino(input)
                game = blackjack.Game(phenny, input.uid, input.nick)
                for item,string in blackjack.help.items():
                    help[item] = string
                for item,args in blackjack.arguments.items():
                    arguments[item] = args
                    temp_cmds.append(item)
            elif args[0] == "poker" or args[0] == "5poker" or args[0] == "7poker" or args[0] == "poker5" or args[0] == "poker7":
                if len(args) < 2:
                    stakes = "mid"
                else:
                    stakes = args[1]

                if args[0] == "7poker" or args[0] == "poker7":
                    cards = 7
                else:
                    cards = 5

                in_play = True
                join_casino(input)
                game = poker.Game(phenny, input.uid, input.nick, cards, stakes)
                for item,string in poker.help.items():
                    help[item] = string
                for item,args in poker.arguments.items():
                    arguments[item] = args
                    temp_cmds.append(item)
        starting = False
start.commands = ['start']
start.priority = 'low'

##################################################################
# Only accept the following commands if there is an ongoing game #
##################################################################

# Join the currently running game
def joingame(phenny, input):
    join_casino(input)
    if in_play and not game.started:
        phenny.say(game.join(input.uid))
joingame.commands = ['enter', 'join']
joingame.priority = 'high'

# Leave the currently running game early
def leave(phenny, input):
    global leaving
    if in_play and game.started and input.uid in p.in_game:
        if input.uid not in leaving:
            leaving.append(input.uid)
            Timer(30.0, cancel_leave, [input.uid]).start()
            phenny.say("Are you sure you want to forfeit all bets and leave the game early? !Yes or !No?")
        else:
            phenny.say("To leave the game respond !Yes")
    elif in_play and not game.started and input.uid in p.in_game:
        p.remove_from_game(input.uid)
        phenny.say("%s left the game." % p.players[input.uid].name)
        if len(p.in_game) == 0:
            game.game_over()
leave.commands = ['leave']
leave.priority = 'high'

# Confirmation functions for responding to leave confirmation msg
def yes(phenny, input):
    if input.uid in leaving:
        if game.started and input.uid in p.in_game:
            p.remove_from_game(input.uid)
            phenny.say("%s forfeit their bet and left the game early." % p.players[input.uid].name)
            if len(p.in_game) == 0:
                game.game_over()
        elif input.uid in p.in_game:
            p.remove_from_game(input.uid)
            phenny.say("%s forfeit their bet and left the game early." % p.players[input.uid].name)
            if len(p.in_game) == 0:
                game.game_over()
yes.commands = ['yes', 'Yes']
yes.priority = 'high'

def no(phenny, input):
    if in_play and input.uid in leaving:
        cancel_leave(input.uid)
        phenny.write(('NOTICE', input.nick + " Thank you. Leave request cancelled."))  # NOTICE
no.commands = ['no', 'No']
no.priority = 'low'

# Place a bet
def bet(phenny, input):
    if in_play and game.accept_bets and input.uid in p.in_game:
        args = check_args(phenny, input.group(0))
        if not args:
            return

        if args[0].isdigit():
            amount = int(args[0])
            game.bet(input.uid, amount)
        else:
            phenny.say("You can only bet with a positive, non-decimal amount of gold. Ex. !bet 100")
    elif in_play and input.uid in p.in_game:
        phenny.write(('NOTICE', input.nick + " There is currently no betting round ongoing."))  # NOTICE
    elif in_play:
        phenny.write(('NOTICE', input.nick + " You are not in the current game.")) # NOTICE
bet.commands = ['bet']
bet.priority = 'high'

# Bet all your gold
def allin(phenny, input):
    if in_play and game.accept_bets and input.uid in p.in_game:
        amount = p.players[input.uid].gold
        phenny.say(p.players[input.uid].place_bet(amount))
    elif in_play:
        phenny.write(('NOTICE', input.nick + " There is currently no betting round ongoing."))  # NOTICE
allin.commands = ['allin']
allin.priority = 'high'

# See all bets
def bets(phenny, input):
    if in_play:
        phenny.say(p.list_bets())
bets.commands = ['bets']
bets.priority = 'low'

# View your hand
def hand(phenny, input):
    if in_play and input.uid in p.in_game:
        phenny.write(('NOTICE', " Your Hand: %s" % p.players[input.uid].hand))
    

####################
# HELPER FUNCTIONS #
#################### 

# Join the player to the players list
def join_casino(input):
    if input.nick not in bots and input.uid not in p.players.keys():
        p.add_player(input.uid, input.nick)

# Check amount of args is correct, returns all args or false if incorrect amount
def check_args(phenny, args):
    args = args.split()
    cmd = args[0][1:]
    args.pop(0)
    if len(args) < arguments[cmd]:
        phenny.say(help[cmd])
        return False
    else:
        return args

# For cancelling a !leave command (on !no or timer)
def cancel_leave(uid):
    global leaving
    if uid in leaving:
        index = leaving.index(uid)
        del leaving[index]

# Donate gold to the requests pool
def donate(phenny, force = False):
    global gold
    rand = randint(0,9)
    if force:
        rand = 2
    if not in_play and gold > 0 and rand == 2:
        phenny.callGazelleApi({'amount': gold, 'action': 'donateGold'})
        phenny.say("CasinoBot donated " + str(gold) + " gold to the Request Pool.")
        gold = 0


if __name__ == '__main__':
    print(__doc__)
