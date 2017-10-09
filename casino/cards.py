#!/usr/bin/env python

import random

# Global for cards
SUITS = ("H", "D", 'S', 'C')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'J':10, 'Q':10, 'K':10}


class Card:
    # An object for creating cards with specific suits and ranks
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print "Invalid card: %d%s" % (rank, suit)  # DEBUG

    def __str__(self):
        if self.suit == 'H' or self.suit == 'D':
            return "04{}{}".format(self.rank, self.suit)
        else:
            return "0,01{}{}".format(self.rank, self.suit)


class Deck:
    # An object for building the deck of cards using the Card object
    def __init__(self):
        self.cards = []
        for suit in SUITS:
            for rank in RANKS:
                self.cards.append(Card(suit, rank))

    def __str__(self):
        return "Deck: " + " ".join(str(c) for c in self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop(0)


class Hand:
    # An object for building a players hand, with cards drawn from the deck
    def __init__(self):
        self.cards = []

    def __str__(self):
        return " ".join(str(c) for c in self.cards) + " "
        # FIXME: do we really need a trailing space here?

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self, index):
        return self.cards.pop(int(index))

    def empty_hand(self):
        del self.cards[:]

    def get_value(self):
        # Count ace's as 1 by default, can override this in the various games
        return sum(VALUES[card.rank] for card in self.cards)

    def number_cards(self):
        return ", ".join("{} - {}".format(i, card)
                         for i, card in enumerate(self.cards, 1))


if __name__ == '__main__':
    print(__doc__)
