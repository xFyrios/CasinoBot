import cards
import player

class HalfProxy:
    """
    A class which presents an implementation to proxy to another object,
    barring certain variables which were set up to be local.
    """

    def __getattr__(self, item):
        """
        Return the parent's attributes if not specifically defined
        here.
        """
        return getattr(self.parent, item)

    def __setattr__(self, item, value):
        """
        If we've defined a parent, and we don't have the attribute, then set the 
        parent's copy of it instead of ours. Otherwise, set ours.
        """
        if 'parent' in self.__dict__ and hasattr(self.parent,
                item) and item not in self.__dict__:
            setattr(self.parent, item, value)
        else:
            self.__dict__[item] = value

class SplitHand(HalfProxy, player.Player):

    def __init__(self, player, fake_id):
        """
        Takes in an originating player as the first argument and
        the card to start with as the second
        """
        #start off with the original bet
        self.bet = player.bet
        self.hand = cards.Hand()
        #split the hand between self and parent
        self.hand.add_card(player.hand.remove_card(1))
        self.fake_id = fake_id
        self.in_game = True
        self.parent = player

    def remove_from_game(self):
        player.remove_from_game(self.fake_id)
