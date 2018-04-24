#! /usr/bin/python
from casino.blackjack import Game
from types import MethodType
import casino.blackjack as b
from casino.player import Player
import casino.player as p
import casino.cards as c
from casino.cards import Card as C
from contextlib import contextmanager
import sys

results = open("results.txt", 'w')

@contextmanager
def test_banner(words):
    old = sys.stdout
    sys.stdout = results
    print "------------------------------------------"
    print words
    print "------------------------------------------"
    yield sner
    sys.stdout = old
    

##################
#redefinig output so can be read on a terminal
def no_color(self):
    return "{}{}".format(self.rank, self.suit)

def no_blank(self):
    dealer = str(p.players[0].hand).split(" ")
    dealer[0] = "XX"
    dealer = " ".join(dealer)
    return dealer

c.Card.__str__ = no_color
b.Game.show_dealers_hand = no_blank

#######################
#A fake phenny to print to terminal
class FakePhenny:
    def write (self, arg):
        print "/%s %s" % (arg[0], arg[1])

    def say (self, arg):
        print arg

##################################
#removing dependency on casino

def game_over(self):
    del p.in_game[:]
    del p.players[0]
    if self.t and self.t.is_alive():
        self.t.cancel()
        self.t = False
    for uid in p.players:
        p.players[uid].bet = 0
        p.players[uid].in_game = False
        p.players[uid].hand.empty_hand()
    self.phenny.say("Game Over!")
    del self

b.casino.gold= 0

def make_game(uid, nick):
    game = Game(FakePhenny(), uid, nick)
    game.game_over = MethodType(game_over, game)
    return game

###############################
#set up fixed cards for testing

def deal(gobble, amount):
    sner = [p.players[0]] + players
    for uid in sner:
        for i in range(amount):
            p.players[uid.uid].hand.add_card(deck.deal_card())

p.deal = deal

def setup_deck(card_list):
    card_objects = []
    rank = ""
    for i in card_list:
        if i in c.SUITS:
            card_objects.append(C(i, rank))
            rank = ""
        else:
            if i != ',':
                rank += i 

    deck = c.Deck() 
    deck.cards += deck.cards
    for i in card_objects[::-1]:
        deck.cards.insert(0,i)
    return deck

##########################################
#actual game setup

b.DELAY_TIME = 0.5

#The Players
guy = Player("guy", "pie")
players = [ guy,
            Player("veesh"  , "veesh"),
            Player("squeesh", "squessh"),
            ]

for i in players:
    i.add_gold(500)
    p.add_player(i.uid, i.name)

##########################################
# Actual Testing!
deck = setup_deck("AS,7H,AC,AS,10H,10S,4H,4S,4C,5D,5H,10S,AH,3C,4H,10H")

sner = make_game(guy.uid, guy.name)
for i in players:
    sner.join(i.uid)
    sner.bet(i.uid, 100)

sner.t.cancel()
sner.deal_cards()
sner.deck = deck

with test_banner("Basic Split"):
    sner.split(players[2].uid)

with test_banner("Split After Split"):
    sner.split(players[2].uid)

with test_banner("Hand as actual player"):
    sner.hand(players[2].uid)

with test_banner("Hand as other player"):
    sner.hand(players[1].uid)

with test_banner("DoubleDown after Split"):
    sner.doubledown(players[2].uid)

with test_banner("Hand as split player"):
    sner.hand(players[2].uid)

sner.stand(players[2].uid)
sner.stand(players[2].uid)
with test_banner("Player 2 splits"):
    sner.split(players[1].uid)

with test_banner("Player 2 loses"):
    sner.hit(players[1].uid)
