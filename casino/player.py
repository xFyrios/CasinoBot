#!/usr/bin/env python

import cards
import sqlite as sql

# This is nasty... but we're keeping the DB object in here for now until the bot gets rewritten
database = False # Holds the sqlite database

# Global players dictionary for holding currently playing users
players = dict()
in_game = []


class Player:
    # An object for building players
    def __init__(self, uid, name, gold = 0, stats = dict()):
        self.uid = uid
        self.name = name
        self.gold = gold
        self.bet = 0
        self.hand = cards.Hand()
        self.in_game = False
        self.splits = 0

        if 'Wins' in stats:
            self.wins = int(stats['Wins'])
        else:
            self.wins = 0
        if 'NaturalWins' in stats:
            self.natural_wins = int(stats['NaturalWins'])
        else:
            self.natural_wins = 0
        if 'Losses' in stats:
            self.losses = int(stats['Losses'])
        else:
            self.losses = 0
        if 'Ties' in stats:
            self.ties = int(stats['Ties'])
        else:
            self.ties = 0

        if 'LargestWin' in stats:
            self.largest_win = int(stats['LargestWin'])
        else:
            self.largest_win = 0
        if 'LargestLoss' in stats:
            self.largest_loss = int(stats['LargestLoss'])
        else:
            self.largest_loss = 0


    def __str__(self):
        string = "Player ID: %s  Name: %s  Gold: %d  Wins: %d  Natural Wins: %d  Losses: %d  Ties: %d  Largest Win: %d  Largest Loss: %d" % (self.uid, self.name, self.gold, self.wins, self.natural_wins, self.losses, self.ties, self.largest_win, self.largest_loss)
        if self.bet > 0:
            string += "  Bet: %d" % self.bet
        return string

    def join_game(self):
        self.in_game = True

    def leave_game(self):
        self.in_game = False

    def add_gold(self, gold):
        global database
        if isinstance(gold, (int, long, float)) or gold.isdigit():
            gold = int(gold)
            if self.uid != 0:
                try: 
                    newgold = self.gold + gold
                    updated = sql.query(database, "UPDATE users SET Gold = ? WHERE UserID=?", (newgold, self.uid))
                    if updated:
                        self.gold = newgold
                except Exception:
                    return False
            else:
                self.gold += gold
            return True

    def remove_gold(self, gold):
        global database
        if isinstance(gold, (int, long, float)) or gold.isdigit():
            gold = int(gold)
            if gold > self.gold:
                gold = self.gold
            if self.uid != 0:
                try:
                    newgold = self.gold - gold
                    updated = sql.query(database, "UPDATE users SET Gold = ? WHERE UserID=?", (newgold, self.uid))
                    if updated:
                        self.gold = newgold
                except Exception:
                    return False
            else:
                self.gold -= gold
            return True

    def place_bet(self, amount):
        amount = int(amount)
        if amount > self.gold:
            return 'You do not have enough gold to make that bet!'
        else:
            self.remove_gold(amount)
            self.bet += amount
            return '%s placed a bet of %d gold. They have %d gold left.' % (self.name, amount, self.gold)

    def remove_from_game(self):
        remove_from_game(self.uid)

    # Functions for winning/losing/ties
    def win_natural(self, phenny):
        self.natural_wins += 1
        winnings = self.bet * 1.5
        self.add_gold(winnings + self.bet)
        self.bet = 0
        self.remove_from_game()
        if self.largest_win < winnings:
            self.largest_win = winnings
        phenny.callGazelleApi({'uid': self.uid, 'gold': winnings, 'action': 'increaseNaturalWins'})
        phenny.write(('NOTICE', self.name + " You won " + str(winnings) + " gold!"))  # NOTICE
        return "%s has a natural blackjack! They won %d gold (1.5x bet)! They now have %d gold." % (self.name, winnings, self.gold)

    def win(self, phenny, amount):
        self.wins += 1
        self.add_gold(amount)
        winnings = amount - self.bet
        self.bet = 0
        self.remove_from_game()
        if self.largest_win < winnings:
            self.largest_win = winnings
        phenny.callGazelleApi({'uid': self.uid, 'gold': winnings, 'action': 'increaseWins'})
        phenny.write(('NOTICE', self.name + " You won " + str(winnings) + " gold!"))  # NOTICE
        return "%s beat the dealer! They won %d gold! They now have %d gold." % (self.name, winnings, self.gold)

    def lose(self, phenny):
        self.losses += 1
        if 0 in players:
            players[0].add_gold(self.bet)
        bet = self.bet
        self.bet = 0
        self.remove_from_game()
        if self.largest_loss < bet:
            self.largest_loss = bet
        phenny.callGazelleApi({'uid': self.uid, 'gold': bet, 'action': 'increaseLosses'})
        phenny.write(('NOTICE', self.name + " You lost your bet of " + str(bet) + " gold. You have " + str(self.gold) + " left."))  # NOTICE

    def tie(self, phenny):
        self.ties += 1
        self.add_gold(self.bet)
        self.bet = 0
        self.remove_from_game()
        phenny.callGazelleApi({'uid': self.uid, 'action': 'increaseTies'})
        phenny.write(('NOTICE', self.name + " Your bet was returned to you."))  # NOTICE

# This will hold the DB
class PlayerDB(object):
    pass


# BASIC FUNCTIONS
def add_player(phenny, uid, nick):
    global database
    # I told you this is nasty...
    if (not database):
        database = PlayerDB()
        sql.setup_db(database)

    if uid != 0:
        if uid in players:
            # Already added
            return True
        gold = sql.query(database, 'SELECT Gold FROM users WHERE UserID=?', uid)
        if gold:
            # user exists in db
            stats = phenny.callGazelleApi({'uid': uid, 'action': 'casinoUserStats'})
            if not stats:
                stats = dict()
            players[uid] = Player(uid, nick, int(gold['Gold']), stats)
            return True
        else:
            inserted = sql.query(database, "INSERT INTO users (UserID, Gold) VALUES (?, 0)", uid)
            if inserted:
                players[uid] = Player(uid, nick, 0)
                return True
            else:
                return False
    else:
        players[uid] = Player(uid, nick)
        return True


def remove_player(uid):
    del players[uid]

def name_to_uid(name):
    for uid in players:
        if players[uid].name.lower() == name.lower():
            return uid
    else:
        return None


def list_players():
    player_names = ''
    for uid in players:
        player_names += players[uid].name + ', '
    return "All Players: %s" % player_names[:-2]


def list_bets():
    all_bets = ''
    for uid in in_game:
        all_bets += players[uid].name + " - " + str(players[uid].bet) + "  "
    return "All Bets: %s " % all_bets[:-2]


# IN-GAME FUNCTIONS
def add_to_game(phenny, uid):
    uid = uid
    if uid in players.keys():
        if uid in in_game:
            return "You already joined the game!"
        else:
            in_game.append(uid)
            players[uid].in_game = True
            # If player hasn't bought in yet, suggest they do
            if players[uid].gold == 0:
                phenny.write(('NOTICE', players[uid].name + " You have joined the game but not bought in yet. Use '!buy amount' to buy in."))  # NOTICE
            return "%s joined the game." % players[uid].name


def make_fake_id(uid):
    return str(uid) + "'s split" + str(players[uid].splits)

def remove_from_game(uid): 
    in_game.remove(uid)
    players[uid].in_game = False


def list_in_game():
    player_names = ''
    for uid in in_game:
        player_names += players[uid].name + ', '
    return "Players In-Game: %s" % player_names[:-2]


def deal(deck, amount):
    while amount > 0:
        for uid in players:
	    if players[uid].in_game == True or uid == 0:
                players[uid].hand.add_card(deck.deal_card())
        amount -= 1


if __name__ == '__main__':
    print(__doc__)
