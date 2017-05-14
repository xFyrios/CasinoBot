#!/usr/bin/env python

import cards as c, player as p
import casino
import time
from threading import Timer
from types import MethodType
from collections import OrderedDict

DELAY_TIME = 30.0

arguments = {'hit': 0, 'stand': 0, 'stay': 0, 'surrender': 0, 'doubledown': 0, 'double': 0}
help = OrderedDict([('hit', "To tell the dealer to give you another card, use the command '!hit'."),
                    ('stand', "To tell the dealer to not give you anymore cards, use the command '!stand'."),
                    ('surrender', "To surrender and give up half of your bet, use the command '!surrender'."),
                    ('doubledown', "To double your bet use the command '!doubledown'. This only works if your "
                                    "hand value is 9, 10, or 11 and it is your first turn. After you will hit once then stand.")])


# Method for calculating a hands value
def hand_value(self):
    # Count ace's as 1, if the hand has an ace, then add 10 if value isn't a bust
    value = 0
    contains_ace = False

    for card in self.cards:
        value += c.VALUES[card.rank]
        if card.rank == 'A':
            contains_ace = True

    if value <= 11 and contains_ace:
        value += 10

    return value


class Game:
    # The main game object for blackjack
    def __init__(self, phenny, uid, nick):
        self.game_type = "blackjack"
        self.started = False
        self.deck = False
        self.accept_bets = False
        self.accept_surrender = False
        self.accept_doubledown = False
        self.t = False  # Used for the delay timer so that we can reset it from the !join command
        self.timer_start = 0  # Used for calculating whether or not we should reset the timer on !join
        self.starter_uid = False
        self.turns = False # The users who have turns, in order, current is at index 0
        self.phenny = phenny

        p.add_player(0, 'Dealer')
        p.players[0].hand.hand_value = MethodType(hand_value, p.players[0].hand)
        p.players[0].add_gold(1000000)
        self.starter_uid = uid

        self.phenny.say("A new game of blackjack has begun! Type !enter if you'd like to play. You have 30 seconds to join.")
        self.phenny.say(p.add_to_game(self.phenny, uid))
        p.players[uid].hand.hand_value = MethodType(hand_value, p.players[uid].hand)
        self.t = Timer(DELAY_TIME, self.begin_game)
        self.timer_start = time.time()
        self.t.start()

    def join(self, uid): 
        if len(p.in_game) < 6 and uid not in p.in_game:
            msg = p.add_to_game(self.phenny, uid)
            # Add the hand_value function
            p.players[uid].hand.hand_value = MethodType(hand_value, p.players[uid].hand)

            # Joining during betting
            if not self.accept_bets:
                # If we are at the max number of players, start the game
                if len(p.in_game) == 6:
                    self.t.cancel()
                    self.begin_game()

                # If half the countdown has already passed, restart the timer
                elif time.time() - self.timer_start > DELAY_TIME / 2 and self.t:
                    self.t.cancel()
                    self.t = Timer(DELAY_TIME, self.begin_game)
                    self.t.start()
            return msg
        elif uid in p.in_game:
            return "You have already joined the game!"
        else:
            return "This game has reached the max amount (6) of players. Please try again later."

    def begin_game(self):
        self.t = False
        self.phenny.say("Welcome to the Casino! This round of blackjack has now begun!")
        if len(p.in_game) > 1:
            self.phenny.say(str("There are %d players this round: %s" % (len(p.in_game), p.list_in_game())))
        else:
            self.phenny.say(str("There is %d player this round: %s" % (len(p.in_game), p.list_in_game())))

        # Place bets
        self.phenny.say("Time to place your initial bets! You have 30 seconds. Use '!bet amount' to bet. You can place multiple bets.")
        self.accept_bets = True
        self.t = Timer(30.0, self.deal_cards)
        self.t.start()

    def bet(self, uid, amount):
        self.phenny.say(p.players[uid].place_bet(amount))

    def deal_cards(self):
        self.t = False
        # Stop betting
        self.accept_bets = False

        # Build the deck and shuffle it
        self.deck = c.Deck()
        self.deck.cards = self.deck.cards + self.deck.cards  # We use 2 decks to give the house a better advantage
        self.deck.shuffle()

        # Deal the cards to the players
        self.phenny.say("The Dealer begins dealing...")
        p.deal(self.deck, 2)

        # Show cards
        for uid in p.in_game:
            self.phenny.write(('NOTICE', p.players[uid].name + " Your Hand: " + str(p.players[uid].hand)))   # NOTICE
        self.show_table()
        self.started = True

        # Check for naturals (an immediate blackjack)
        dealer_win = False
        if p.players[0].hand.hand_value() == 21:
            dealer_win = True
            self.phenny.say("The dealer started with a natural blackjack!")
            self.show_full_table()

        for uid in p.in_game[:]:
            if p.players[uid].hand.hand_value() == 21:
                if dealer_win:
                    p.players[uid].tie(self.phenny)
                    self.phenny.say(str("%s and the dealer both have natural blackjacks. They tie!" % p.players[uid].name))
                else:
                    self.phenny.say(p.players[uid].win_natural(self.phenny))
            elif dealer_win:
                p.players[uid].lose(self.phenny)
                self.phenny.say("%s lost to the dealers natural blackjack." % p.players[uid].name)

        # Play game
        self.play()

    def show_table(self):
        table = 'Table: '
        table += 'Dealer - ' + self.show_dealers_hand() + ' '
        for uid in p.in_game:
            table += p.players[uid].name + " - " + str(p.players[uid].hand) + ' '
        self.phenny.say(table)

    # Shows all of dealers cards
    def show_full_table(self):
        table = 'Table: '
        table += 'Dealer - ' + str(p.players[0].hand) + ' '
        for uid in p.in_game:
            table += p.players[uid].name + " - " + str(p.players[uid].hand) + ' '
        self.phenny.say(table)

    @staticmethod
    def show_dealers_hand():
        dealer = str(p.players[0].hand).split(" ")
        dealer[0] = "1,01XX"
        dealer = " ".join(dealer)
        return dealer

    def play(self):
        if len(p.in_game) == 0:
            self.game_over()  # All players already lost
            return
        p.in_game = p.in_game[::-1]  # Start by reversing the in-game list as the dealer starts on their left

        # Hit or stand? Keep asking until the user stands or busts
        self.turns = p.in_game[:]
        uid = self.turns[0]
        self.accept_surrender = True
        self.set_doubledown(uid)
        if self.accept_doubledown:
            self.phenny.say("%s. !Stand, !Hit, !Surrender, or !DoubleDown?" % p.players[uid].name)
        else:
            self.phenny.say("%s. !Stand, !Hit, or !Surrender?" % p.players[uid].name)
        self.t = Timer(30.0, self.stand, [uid, True])
        self.t.start()

    def hit(self, uid):
        if self.turns and self.turns[0] == uid:
            p.players[uid].hand.add_card(self.deck.deal_card())
            self.phenny.say("Hit. %s: %s" % (p.players[uid].name, str(p.players[uid].hand)))
            if self.t and self.t.is_alive():
                self.t.cancel()
                self.t = False

            if p.players[uid].hand.hand_value() > 21:
                p.players[uid].lose(self.phenny)
                self.phenny.say("BUST! %s went over 21. Their bet was lost to the dealer." % p.players[uid].name)
                del self.turns[0]

            if len(self.turns) > 0 and self.turns[0] == uid: # This players next move
                self.accept_surrender = False
                self.accept_doubledown = False
                self.phenny.write(('NOTICE', p.players[uid].name + " Your Hand: " + str(p.players[uid].hand)))   # NOTICE
                self.phenny.say("Hit. %s. !Stand or !Hit?" % p.players[uid].name)
                self.t = Timer(30.0, self.stand, [uid, True])
                self.t.start()
            elif len(p.in_game) == 0:
                self.show_full_table()
                self.game_over()  # All players lost, end the game
            else:
                self.next_player()

    def stand(self, uid, auto = False):
        if self.turns and self.turns[0] == uid:
            del self.turns[0]

            if auto:
                self.phenny.say("%s took too long. They stand automatically." % p.players[uid].name)
                self.t = False
            elif self.t and self.t.is_alive():
                self.t.cancel()
                self.t = False

            self.next_player()

    def surrender(self, uid):
        if self.accept_surrender and self.turns and self.turns[0] == uid:
            del self.turns[0]

            if self.t and self.t.is_alive():
                self.t.cancel()
                self.t = False
        
            bet = p.players[uid].bet
            p.players[0].add_gold(bet/2)
            p.players[uid].bet = 0
            p.players[uid].add_gold(bet/2)
            p.remove_from_game(uid)
            gold = p.players[uid].gold
            self.phenny.write(('NOTICE', p.players[uid].name + " You surrendered losing half your bet of " + str(bet) + " to the dealer. You have " + str(gold) + " left."))  # NOTICE

            self.next_player()

    def doubledown(self, uid):
        if self.accept_doubledown and self.turns and self.turns[0] == uid:
            bet = p.players[uid].bet
            self.phenny.say(p.players[uid].place_bet(bet))

            p.players[uid].hand.add_card(self.deck.deal_card())
            self.phenny.say("Hit. %s: %s" % (p.players[uid].name, str(p.players[uid].hand)))
            
            if p.players[uid].hand.hand_value() > 21:
                p.players[uid].lose(self.phenny)
                self.phenny.say("BUST! %s went over 21. Their bet was lost to the dealer." % p.players[uid].name)
                self.next_player()
            else:
                self.stand(uid) 

    def set_doubledown(self, uid):
        if p.players[uid].hand.hand_value() in [9,10,11] and int(p.players[uid].gold) >= int(p.players[uid].bet):
            # We allow double downs when hand value is 9,10, or 11 and the player has enough gold to double their bet
            self.accept_doubledown = True

    def next_player(self):
        if len(self.turns) > 0:
            uid = self.turns[0]
            self.accept_surrender = True
            self.set_doubledown(uid)
            self.phenny.write(('NOTICE', p.players[uid].name + " Your Hand: " + str(p.players[uid].hand)))   # NOTICE
            if self.accept_doubledown:
                self.phenny.say("%s. !Stand, !Hit, !Surrender, or !DoubleDown?" % p.players[uid].name)
            else:
                self.phenny.say("%s. !Stand, !Hit, or !Surrender?" % p.players[uid].name)
            self.t = Timer(30.0, self.stand, [uid, True])
            self.t.start()
        else:
            self.accept_surrender = False
            self.accept_doubledown = False
            self.dealer_play() # All turns complete, dealer plays

    def hand(self, uid):
        if uid in p.in_game:
            self.phenny.write(('NOTICE', " Your Hand: %s" % p.players[uid].hand))

    def dealer_play(self):
        self.phenny.say("Alright, Dealers Turn. The dealer flips his card upright...")
        self.phenny.say("Dealer's Hand: " + str(p.players[0].hand))
        while p.players[0].hand.hand_value() < 17:
            p.players[0].hand.add_card(self.deck.deal_card())
            self.phenny.say("Hit. Dealer: " + str(p.players[0].hand))
            if p.players[0].hand.hand_value() > 21:
                self.phenny.say("BUST! The Dealer went over 21. All remaining players win!")
                for uid in p.in_game[:]:
                    p.players[uid].win(self.phenny, (p.players[uid].bet * 2))
                self.game_over()
                break
        else :
            self.phenny.say("Stay. Dealers finishing hand: " + str(p.players[0].hand))
            self.calc_winners()

    def calc_winners(self):
        self.phenny.say("Results for remaining players:")
        self.show_full_table()
        dealer_value = p.players[0].hand.hand_value()

        for uid in p.in_game[:]:
            player_value = p.players[uid].hand.hand_value()
            if dealer_value > player_value or player_value > 21:
                self.phenny.say("Dealer's hand beat %s's hand by %d points." % (p.players[uid].name, dealer_value - player_value))
                p.players[uid].lose(self.phenny)
            elif dealer_value == player_value:
                self.phenny.say("There was a tie between %s and the dealer." % p.players[uid].name)
                p.players[uid].tie(self.phenny)
            else:
                self.phenny.say("%s's hand beat the Dealer's hand by %d points." % (p.players[uid].name, player_value - dealer_value))
                self.phenny.say(p.players[uid].win(self.phenny, (p.players[uid].bet * 2)))
        self.game_over()  # Now end the game

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

        # Update casino's game variables
        casino.game = False
        casino.in_play = False
        for item in casino.temp_cmds:
            if item in casino.help:
                del casino.help[item]
            if item in casino.arguments:
                del casino.arguments[item]


if __name__ == '__main__':
    print(__doc__)
