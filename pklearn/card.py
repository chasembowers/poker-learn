from deuces import deuces

class Card:
    
    nEnum = {'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}
    suits = ['c', 'd', 's', 'h']

    def __init__(self, numLet, suit):

        """ Constructor accepts number [2-14] or letter (T,J,Q,K,A) of card and suit of card (c,d,s,h). """

        if type(numLet) == int:
            if numLet < 2 or numLet > 14: raise Exception('Card number must be between 2 and 14 (inclusive).')
            self._numLet = numLet
            for k in self.nEnum:
                if self.nEnum[k] == numLet: self._numLet = k
        elif type(numLet) == str:
            if numLet.upper() not in self.nEnum: raise Exception("Card letter must be \'T\', \'J\', \'Q\', \'K\', or \'A\'.")
            self._numLet = numLet.upper()
        else: raise Exception('Card number/letter must be number or string.')

        if suit.lower() not in self.suits: raise Exception("Invalid suit. Valid suits are \'c\', \'d\', \'s\', and \'h\'.")
        self._suit = suit.lower()

    def getNumber(self):
        
        """ This method returns number of card. It converts letter to number if necesary. """
        
        if self._numLet in self.nEnum: return self.nEnum[self._numLet]
        return self._numLet

    def getSuit(self): return self._suit

    def toInt(self): return deuces.Card.new(str(self)) #returns int compatible with deuces library

    def __lt__(self, other): return self.getNumber() < other.getNumber()

    def __str__(self): return str(self._numLet) + self._suit

        




        


