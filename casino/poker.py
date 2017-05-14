#!/usr/bin/env python

import cards as c, player as p
import casino
import time
import deuces
from threading import Timer
from collections import OrderedDict

DELAY_TIME = 30.0

arguments = {'ante': 0, 'raise': 0, 'check': 0, 'call': 0, 'fold': 0, 'discard': 1, 'pass': 0}
help = OrderedDict([('ante', "Used to buy into a game after you join. If you do not ante-in you will be parted from the game when it begins."),
                    ('raise', "Match the current highest bet and raise it by a certain amount. Used during a betting round after the first bet has been made. Ex. !raise 20"),
                    ('check', "Don't increase the bet and pass onto the next player. Used during a betting round when your bet matches the highest bet."),
                    ('call', "Match the current highest bet and pass onto the next player. Used during a betting round when there is a higher bet than yours on the table."),
                    ('fold', "Leave the game and lose your current bet. Used during a betting round when you would rather forfeit than raise your bet."),
                    ('discard', "Used to discard a card and have it replaced during the draw round. When it is your turn to discard, the bot will msg you with your hand "
                                "and a numeric value (ex. 1 - JC) for each card. To discard type '!discard # #', where # is the numeric value of the card you wish to have "
                                "replaced. Ex. !discard 1, would discard the Jack of Clubs from the previous example. To discard multiple, seperate each number with a space."),
                    ('pass', "Used during the draw round to pass and not discard any cards.")])

class Game:
    # The main game object for poker
    def __init__(self, phenny, uid, nick, cards, stakes):
        self.game_type = "poker"
        self.started = False
        self.deck = False
        self.deck2 = False
        self.can_join = False
        self.accept_bets = False
        self.accept_discard = False
        self.current_bet = 0
        self.betting_rounds = 0
        self.betting_stage = False
        self.betting_pot = 0
        self.opening_player = False
        self.num_cards = cards
        self.accept_ante = True
        self.t = False # Used for the delay timer so that we can reset it from the !join command
        self.timer_start = 0  # Used for calculating whether or not we should reset the timer on !join
        self.starter_uid = uid
        self.turns = False
        self.phenny = phenny

        if stakes.isdigit():
            self.stakes = int(stakes)
        elif stakes == "free":
            self.stakes = "free"
        elif stakes == "low":
            self.stakes = 100
        elif stakes == "high":
            self.stakes = 5000
        elif stakes == "extreme":
            self.stakes = 50000
        else:
            self.stakes = 500

        self.phenny.say("A new game of " + str(self.num_cards) + " card poker has begun! Type !enter if you'd like to play. You have 30 seconds to join.");
        if self.stakes == "free":
            self.phenny.say("This is a no stakes game. There are no ante's and betting is not permitted.");
        else:
            self.phenny.say("The ante for this game is set at " + str(self.stakes) + " gold. After joining please type !ante to buy into the game.");

        self.phenny.say(p.add_to_game(self.phenny, uid))
        p.players[uid].ante = False
        self.can_join = True

        self.t = Timer(DELAY_TIME, self.begin_game)
        self.timer_start = time.time()
        self.t.start()
        
    def join(self, uid):
        if not self.can_join:
            self.phenny.say("%s, this game has already started!" % p.players[uid].name)
            return
        if len(p.in_game) < 6 and uid not in p.in_game:
            msg = p.add_to_game(self.phenny, uid)
            p.players[uid].ante = False

            # If half the countdown has already passed, restart the timer
            if len(p.in_game) != 6 and time.time() - self.timer_start > DELAY_TIME / 2 and self.t:
                self.t.cancel()
                self.t = Timer(DELAY_TIME, self.begin_game)
                self.t.start()
            # If less than 5 seconds left, bump the timer to 5 seconds no matter what so the new player has time to ante
            elif time.time() - self.timer_start > DELAY_TIME - 5.0 and self.t:
                self.t.cancel()
                self.t = Timer(5.0, self.begin_game)
                self.t.start()
            return msg
        elif uid in p.in_game:
            return "You have already joined the game!"
        else:
            return "This game has reached the max amount (6) of players. Please try again later."

    def ante(self, uid, nick = ''):
        if not self.can_join:
            self.phenny.say("%s, this game has already started!" % p.players[uid].name)
            return
        if uid not in p.players.keys():
            p.add_player(uid, nick)
        if self.accept_ante == True and self.stakes != "free":
            if uid not in p.in_game:
                self.join(uid)
            if p.players[uid].ante == True:
                self.phenny.say("%s, you already ante'd into this game." % p.players[uid].name);
            elif p.players[uid].gold < self.stakes:
                self.phenny.say("%s, you do not have enough gold to ante into this game. Use !buy to transfer more gold from the site." % p.players[uid].name)
            else:
                p.players[uid].place_bet(self.stakes)
                p.players[uid].ante = True
                self.betting_pot += self.stakes
                self.phenny.say("%s ante'd in with %d gold. They have %d gold left." % (p.players[uid].name, self.stakes, p.players[uid].gold))
        else:
            self.phenny.say("Ante's are not currently being accepted.");

    def begin_game(self):
        self.t = False
        self.can_join = False
        self.phenny.say("Welcome to the Casino! This round of " + str(self.num_cards) + " card poker has now begun!")
        
        if self.stakes != "free":
            # Remove users that didnt ante in
            for uid in p.in_game:
                if p.players[uid].ante == False:
                    p.remove_from_game(uid)
                    self.phenny.say("%s did not ante in and was removed from this game." % p.players[uid].name)
            if len(p.in_game) == 0:
                self.phenny.say("No players ante'd in.")
                self.game_over()
                return

        if len(p.in_game) > 1:
            self.phenny.say(str("There are %d players this round: %s" % (len(p.in_game), p.list_in_game())))
        # Not enough players
        else:
            self.phenny.say("There are not enough players! For a game of poker there must be 2 players minimum.")
            for uid in p.in_game:
                p.players[uid].add_gold(p.players[uid].bet)
                p.players[uid].bet = 0
                p.remove_from_game(uid)
                self.phenny.write(('NOTICE', p.players[uid].name + " The dealer returned your ante."))
            self.game_over()
            return

        self.deal_cards()

    def deal_cards(self):
        # Build the deck and shuffle it
        self.deck = c.Deck()
        self.deck.shuffle()
        # Extra deck used for holding discarded cards
        self.deck2 = c.Deck()
        del self.deck2.cards[:]

        # Deal the cards to the players
        self.phenny.say("The dealer begins dealing...")
        p.deal(self.deck, self.num_cards)

        for uid in p.in_game:
            self.phenny.write(('NOTICE', p.players[uid].name + " Your Hand: %s" % p.players[uid].hand))

        p.in_game = p.in_game[::-1]
        self.phenny.say("The dealer has dealt each player " + str(self.num_cards) + " cards.")

        self.betting_stage = 1
        if self.stakes != "free":
            self.betting_round()
        else:
            self.draw_round()

    def betting_round(self):
        self.accept_bets = True
        self.betting_rounds += 1
        self.turns = p.in_game[:]
        if self.betting_stage == 1 and self.betting_rounds == 1:
            self.phenny.say("The initial betting round has begun. Place your bets! The max total bet is %d gold." % (self.stakes * 5))
        elif self.betting_stage == 2 and self.betting_rounds == 1:
            self.phenny.say("The final betting round has begun. Place your bets! The max total bet is %d gold." % (self.stakes * 10))
            self.phenny.say("The current bet is at %d gold." % self.current_bet)

        uid = self.turns[0]
        options = self.betting_options(uid)
        if self.current_bet > 0:
            self.phenny.say("%s,%s? The current bet is at %d gold." % (p.players[uid].name, options, self.current_bet))
        else:
            self.phenny.say("%s,%s?" % (p.players[uid].name, options))

        if self.accept_check(uid):
            self.t = Timer(30.0, self.check, [uid, True])
        else:
            self.t = Timer(30.0, self.fold, [uid, True])
        self.t.start()

    def raise_bet(self, uid, amount):
        if self.accept_bets and self.turns and self.turns[0] == uid and self.betting_rounds < 3:
            new_bet = (self.current_bet - p.players[uid].bet + self.stakes) + int(amount)
            self.bet(uid, new_bet)

    def bet(self, uid, amount):
        if self.accept_bets and self.turns and self.turns[0] == uid and self.betting_rounds < 3:
            # Calculate max bet
            if self.betting_stage == 1:
                max_bet = self.stakes * 5
            else:
                max_bet = self.stakes * 10
            max_bet += self.stakes

            if (p.players[uid].bet + amount) <= max_bet:
                if (p.players[uid].bet + amount) > self.current_bet:
                    if p.players[uid].gold >= amount:
                        # New bet
                        self.t.cancel()
                        self.t = False
                        original_bet = self.current_bet
                        p.players[uid].place_bet(amount)
                        self.betting_pot += amount
                        self.current_bet = (p.players[uid].bet - self.stakes)
                        if original_bet == 0:
                            self.opening_player = uid
                            self.phenny.say("%s opened the bet at %d gold. They have %d gold left." % (p.players[uid].name, self.current_bet, p.players[uid].gold))
                        else:
                            self.phenny.say("%s raised the bet to %d gold. They have %d gold left." % (p.players[uid].name, self.current_bet, p.players[uid].gold))
                        self.next_bet()
                    else:
                        self.phenny.say("You do not have enough gold to make that bet!")
                        if self.t and self.t.is_alive():
                            self.t.cancel()
                            if self.accept_check(uid):
                                self.t = Timer(30.0, self.check, [uid, True])
                            else:
                                self.t = Timer(30.0, self.fold, [uid, True])
                            self.t.start()
                elif (p.players[uid].bet + amount) == self.current_bet:
                    self.check(uid, False)
                else:
                    self.phenny.say("Your bet must either meet or exceed the current highest bet. Either bet %d+ gold, or !fold." % self.current_bet)
                    if self.t and self.t.is_alive():
                        self.t.cancel()
                        if self.accept_check(uid):
                            self.t = Timer(30.0, self.check, [uid, True])
                        else:
                            self.t = Timer(30.0, self.fold, [uid, True])
                        self.t.start()
            else:
                self.phenny.say("Your bet exceeds the max bet for this round. The total bet per person cannot go over %d gold." % (max_bet - self.stakes))
                if self.t and self.t.is_alive():
                    self.t.cancel()
                    if self.accept_check(uid):
                        self.t = Timer(30.0, self.check, [uid, True])
                    else:
                        self.t = Timer(30.0, self.fold, [uid, True])
                    self.t.start()
                
    def check(self, uid, auto = False):
        if self.accept_bets and self.turns and self.turns[0] == uid and self.accept_check(uid):
            if auto:
                self.phenny.say("%s took too long. They check automatically." % p.players[uid].name)
                self.t = False
            elif self.t and self.t.is_alive():
                self.t.cancel()
                self.t = False

            self.next_bet()

    def accept_check(self, uid):
        if p.players[uid].bet == (self.current_bet + self.stakes):
            return True
        else:
            return False

    def call(self, uid):
        if self.accept_bets and self.turns and self.turns[0] == uid and self.accept_call(uid):
            gold_req = (self.current_bet + self.stakes) - p.players[uid].bet
            
            if gold_req == 0:
                self.check(uid, False)
                return

            if p.players[uid].gold >= gold_req:
                p.players[uid].place_bet(gold_req)
		self.betting_pot += gold_req
                self.phenny.say("%s called with %d gold to meet the current bet of %d gold. They have %d gold left." % (p.players[uid].name, gold_req, self.current_bet, p.players[uid].gold))
                if self.t and self.t.is_alive():
                    self.t.cancel()
                    self.t = False
                # If 3rd round and everyone left can check then move onto draw round
                if self.betting_rounds == 3:
                    end_round = True
                    for uid in self.turns:
                        if not self.accept_check(uid):
                            end_round = False
                            break
                    if end_round:
                        del self.turns[:]
                        self.turns.append(0)
                self.next_bet()
            else:
                self.phenny.say("You do not have enough gold left to call. You can !buy more to transfer funds from the site and then try again.")
                if self.t and self.t.is_alive():
                    self.t.cancel()
                    self.t = Timer(30.0, self.fold, [uid, True])
                    self.t.start()

    def accept_call(self, uid):
        print "uid: " + str(uid) + " current_bet: " + str(self.current_bet) + " stakes: " + str(self.stakes) + " my bet: " + str(p.players[uid].bet)
        if (self.current_bet + self.stakes) > p.players[uid].bet:
            return True
        else:
            return False

    def fold(self, uid, auto = False):
        if self.accept_bets and self.turns and self.turns[0] == uid:
            if auto:
                self.phenny.say("%s took too long. They fold automatically." % p.players[uid].name)
                self.t = False
            elif self.t and self.t.is_alive():
                self.phenny.say("%s folded and left the game." % p.players[uid].name)
                self.t.cancel()
                self.t = False

            p.players[uid].lose(self.phenny)

            if len(p.in_game) == 1:
                self.game_over()
            else:
                self.next_bet()


    def next_bet(self):
        del self.turns[0]
        if self.t and self.t.is_alive():
            self.t.cancel()
            self.t = False

        if len(self.turns) == 0:
            new_round = False
            for uid in p.in_game:
                if p.players[uid].bet != (self.current_bet + self.stakes):
                    new_round = True
                    break
            if new_round:
                self.betting_round()
            else:
                if self.betting_stage == 1:
                    self.draw_round()
                else:
                    self.game_over()
            return

        uid = self.turns[0]
        options = self.betting_options(uid)
        self.phenny.say("%s,%s? The current bet is at %d gold." % (p.players[uid].name, options, self.current_bet))
        if self.accept_call(uid):
            self.phenny.write(("NOTICE", p.players[uid].name + " Your current bet: " + str(p.players[uid].bet - self.stakes) + ". You must bet " + str(self.current_bet - (p.players[uid].bet - self.stakes)) + " to proceed."))
        else:
            self.phenny.write(("NOTICE", p.players[uid].name + " Your current bet: " + str(p.players[uid].bet - self.stakes)))

        if self.accept_check(uid):
            self.t = Timer(30.0, self.check, [uid, True])
        else:
            self.t = Timer(30.0, self.fold, [uid, True])
        self.t.start()

    def betting_options(self, uid):
        options = ""

        if self.betting_rounds < 3:
            if self.current_bet == 0:
                options += " !bet"
            else:
                options += " !raise"
        if self.betting_rounds < 3 and self.accept_call(uid):
            options += ","
        if self.accept_call(uid):
            options += " !call"
        if self.accept_check(uid):
            options += " or !check"
        else:
            options += " or !fold"

        return options

    def draw_round(self):
        if len(p.in_game) == 0:
            self.game_over()
        self.accept_bets = False
        self.turns = p.in_game[:]
        self.phenny.say("Initial betting round complete. The Draw round will now commence.")

        uid = self.turns[0]
        self.phenny.say("%s, you're up first. Would you like to discard any cards? If not, say !pass." % p.players[uid].name)
        self.phenny.say("To discard cards, type '!discard # # #' where # is the number of a card in your hand. To discard multiple, seperate each with a space.")
        self.phenny.write(("NOTICE", p.players[uid].name + " Your cards: " + p.players[uid].hand.number_cards()))
        
        self.accept_discard = True
        self.t = Timer(60.0, self.pass_discard, [uid, True])
        self.t.start()

    def discard(self, uid, cards):
        if self.accept_discard and self.turns and self.turns[0] == uid:
            del self.turns[0]
            
            if self.t and self.t.is_alive():
                self.t.cancel()
                self.t = False

            # Order in desc order before removing so we dont lose original positions
            cards.sort(key=int)
            cards.reverse()

            i = 0
            for index in cards:
                self.deck2.cards.append(p.players[uid].hand.remove_card(int(index)-1))
                i += 1
            cards_discarded = i
            while i > 0:
                if len(self.deck.cards) == 0:
                    self.deck = self.deck2
                p.players[uid].hand.add_card(self.deck.deal_card())
                i -= 1

            self.phenny.say("%s discarded %d cards." % (p.players[uid].name, cards_discarded))
            self.phenny.write(("NOTICE", p.players[uid].name + " Your new hand: " + str(p.players[uid].hand)))
            self.next_player()

    def pass_discard(self, uid, auto = False):
        if self.accept_discard and self.turns and self.turns[0] == uid:
            del self.turns[0]
        
            if auto:
                self.phenny.say("%s took too long. They pass automatically." % p.players[uid].name)
                self.t = False
            elif self.t and self.t.is_alive():
                self.t.cancel()
                self.t = False

            self.next_player()
        
    def next_player(self):
        if len(self.turns) > 0:
            uid = self.turns[0]
            self.phenny.say("%s, would you like to discard any cards?" % p.players[uid].name)
            self.phenny.write(("NOTICE", p.players[uid].name + " Your cards: " + p.players[uid].hand.number_cards()))
            self.t = Timer(30.0, self.pass_discard, [uid, True])
            self.t.start()
        else:
            self.betting_stage = 2
            self.betting_rounds = 0
            if self.stakes != "free":
                if self.opening_player:
                    index = p.in_game.index(self.opening_player)
                    p.in_game = p.in_game[index:] + p.in_game[:index]
                self.betting_round()
            else:
                self.game_over()
            
    def show_table(self):
        table = 'Table: '
        for uid in p.in_game:
            table += p.players[uid].name + " - " + str(p.players[uid].hand) + ' '
        self.phenny.say(table)

    def get_winner(self):
        evaluator = deuces.Evaluator()
        winner = 0
        best_score = 8000
        scores = "Each hand has been scored:"
        for uid in p.in_game:
            hand = []
            #Generate a hand that the deuces module understands
            for card in p.players[uid].hand.cards:
                rank = str(card.rank)
                if rank == '10':
                    rank = 'T'
                suit = card.suit.lower()
                print rank + suit
                hand.append(deuces.Card.new(rank + suit))
            print uid + ": " + str(hand)
            p.players[uid].score = evaluator.evaluate([], hand)
            p.players[uid].rank_class = evaluator.get_rank_class(p.players[uid].score)
            if p.players[uid].score < best_score:
                best_score = p.players[uid].score
                winner = uid
            print "score: " + str(p.players[uid].score)
            print "rank: " + str(p.players[uid].rank_class)
            print "class: " + str(evaluator.class_to_string(p.players[uid].rank_class))
            print ''
            scores = scores + " " + p.players[uid].name + " - " + str(evaluator.class_to_string(p.players[uid].rank_class)) + ","
        del evaluator
        scores = scores[:-1]
        self.phenny.say(scores)
        
        winnings = self.betting_pot - p.players[winner].bet
        print "pot: " + str(self.betting_pot) + " winners bet: " + str(p.players[winner].bet) + " winnings: " + str(winnings)
        p.players[winner].win(self.phenny, self.betting_pot)
        self.phenny.say("%s has the highest ranking hand! They won %d gold! They now have %d gold." % (p.players[winner].name, winnings, p.players[winner].gold))
            
    
    def game_over(self):
        if self.t and self.t.is_alive():
            self.t.cancel()
            self.t = False

        if len(p.in_game) == 1:
            uid = p.in_game[0]
            winnings = self.betting_pot - p.players[uid].bet 
            p.players[uid].win(self.phenny, self.betting_pot)
            self.phenny.say("%s is the last man standing! They won %d gold! They now have %d gold." % (p.players[uid].name, winnings, p.players[uid].gold))
        elif len(p.in_game) > 1:
            self.phenny.say("Alright, time for the showdown! Show your cards!")
            self.show_table()
            uid = self.get_winner()
            
        del p.in_game[:]
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
