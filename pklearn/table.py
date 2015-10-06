from player import Player
from random import shuffle
from card import Card
from deuces.deuces import Evaluator

class Table:    

    """
    This class is primarily responsible for core holdem simulation logic. Basic usage consists of 
    adding players via addPlayer() and simulating via play(). For simplicity, betting takes place
    with integer number of chips with uniform value.
    """

    def __init__(self, smallBlind, bigBlind, maxBuyIn):

        """ Constructor accepts  blinds and maximum table buy in as integers. """
        
        self._players = []  #players at the table
        self._playing = []  #players who are not bankrupt
        self._sitOut = []   #players who have gone bankrupt
        self._dealer = 0    #position of dealer in self._playing
        self._eval = Evaluator()

        if type(smallBlind) != int or type(bigBlind) != int or type(maxBuyIn) != int:
            raise Exception('Parameters must be integer number of chips.')
        self._smallBlind = smallBlind
        self._bigBlind = bigBlind
        self._maxBuyIn = maxBuyIn

    def addPlayer(self, player):

        self._sitOut.append(player)
        self._players.append(player)

    def playHand(self, vocal=False):

        """ 
        This method simulations one hand between added players. Narrates hand if vocal is True.
        Returns False if unable to play hand. 
        """

        self._vocal = vocal

        #add players to hand who are eligible to play
        for p in self._sitOut[:]:
            if p.getStack() >= self._bigBlind:
                if p.getStack() > self._maxBuyIn: 
                    raise Exception('Player\'s stack is greater than maximum buy in.')
                self._playing.append(p)
                self._sitOut.remove(p)

        if len(self._playing) <= 1: return False
            
        #reset table game state before hand
        self._s = {
                        #amount of chips necessary to call without going all-in
                        'toCall': None,                           
                        
                        #minimum raise size, player must increase bet to minRaise to raise
                        'minRaise': None,                         
                        
                        #number of players in hand
                        'numP': len(self._playing),               
                        
                        #total contribution of each player to completed betting rounds
                        #by position of player in self._playing  
                        #sum of bets is total pot excluding current betting round
                        'bets': [0 for p in self._playing],       
                        
                        #total contribution of each player to pot of current betting round
                        #sum of currBets is total pot of current round
                        #sum of bets and currBets is total pot
                        'currBets': [0 for p in self._playing],   
                        
                        #list of positions where players have folded
                        'folded': [],
                        
                        #list of positions where players are all-in
                        'allIn': [],                                    
                        
                        #face up community cards
                        'cards': [],                              
                        
                        #index of player who is currently acting in self._playing
                        'actor': None,                             

                        #number of raises this round by position of player
                        'numRaises': [0 for p in self._playing]
                      }    

        #commence simulation
        self._generateDeck()
        self._dealHoleCards()
        self._preFlop()
        self._flip(3)
        self._flip(1)
        self._flip(1)
        self._payWinners()
        for p in self._playing: p.endHand()

        #find next dealer
        dealerPos = (self._dealer + 1) % self._s['numP']
        while self._playing[dealerPos].getStack() < self._bigBlind: 
            dealerPos = (dealerPos + 1) % self._s['numP']
        dealer = self._playing[dealerPos]

        #remove players who have gone bankrupt
        for p in self._playing[:]:
            if p.getStack() < self._bigBlind:
                self._playing.remove(p)
                self._sitOut.append(p)

        #move dealer chip 
        self._dealer = 0
        while self._playing[self._dealer] != dealer: self._dealer = (self._dealer + 1) % self._s['numP']

        if vocal: print
        return True

    def _generateDeck(self):

        self._deck = []
        for s in ['c', 'd', 'h', 's']:
            for i in range(2,15):
                self._deck.append(Card(i,s))
        shuffle(self._deck)
 
    def _dealHoleCards(self):

        """ This method gives each player their starting cards at the beginning of the hand. """

        for p in self._playing:
            p.takeHoleCards((self._deck[0],self._deck[1]))
            if self._vocal: print p.getName() + '(' + str(p.getStack()) + ')', 'dealt', self._deck[0], 'and', self._deck[1]
            self._deck = self._deck[2:]
        if self._vocal: print

    def _preFlop(self):

        """ This method posts the blinds and commences betting. """

        self._s['minRaise'] = 2 * self._bigBlind    #minimum first raise before flop is 2 x Big Blind

        sbPos = (self._dealer + 1) % self._s['numP']    #small blind position
        bbPos = (self._dealer + 2) % self._s['numP']    #big blind position
        self._s['actor'] = (self._dealer + 3) % self._s['numP']    #first player to act

        #Heads-Up (1v1) has different rules prelop
        if self._s['numP'] == 2:    
            sbPos = self._dealer    
            bbPos = (self._dealer + 1) % self._s['numP']
            self._s['actor'] = self._dealer   

        #post blinds
        self._s['currBets'][sbPos] += self._smallBlind
        self._playing[sbPos].removeChips(self._smallBlind)
        if self._vocal: print self._playing[sbPos].getName(), 'posts small blind of', self._smallBlind
        self._s['currBets'][bbPos] += self._bigBlind
        self._playing[bbPos].removeChips(self._bigBlind)
        if self._vocal: print self._playing[bbPos].getName(), 'posts big blind of', self._bigBlind

        self._openBetting()
        if self._vocal: print

    def _flip(self, numCards):  

        """ This method flips numCards cards from deck to be seen by players and then commences betting. """

        if len(self._s['folded']) + 1 == self._s['numP']: return    #all players but one have folded

        self._s['minRaise'] = self._bigBlind    #minimum first bet after the flop is Big Blind

        #flip numCards
        self._s['cards'] += self._deck[:numCards]
        if self._vocal: print [str(c) for c in self._s['cards']]
        self._deck = self._deck[numCards:]
        
        self._s['actor'] = (self._dealer + 1) % self._s['numP']    #first actor is player after dealer
        
        self._openBetting()
        if self._vocal: print

    def _payWinners(self):

        """ This method distributes the pot to the winner(s). """

        board = [card.toInt() for card in self._s['cards']]
        
        #evaluate rank of hand for each player
        ranks = {}
        for p in self._playing:
            if not board: rank = -1    #all players but one have folded before flop
            else: rank = self._eval.evaluate(board, [p.show()[0].toInt(), p.show()[1].toInt()])
            ranks[p] = rank

        n = 0
        while sum(self._s['bets']) > 0:    #to handle n side pots

            #get rank of best hand and bet of each player who is eligible to win sub pot
            minLiveBet = None    #bet that any eligible player has in current sub pot
            minRank = None
            eligibleWinners = []
            for i in range(self._s['numP']):
                if not i in self._s['folded'] and self._s['bets'][i] != 0:    #if player hasnt folded and has stake in current sub pot
                    if minLiveBet == None: minLiveBet = self._s['bets'][i]
                    else: minLiveBet = min(minLiveBet, self._s['bets'][i])
                    player = self._playing[i]
                    eligibleWinners.append(player)
                    if minRank == None: minRank = ranks[player]
                    else: minRank = min(minRank, ranks[player])

            #create sub pot by adding contributions of its members
            winners = [p for p in eligibleWinners if ranks[p] == minRank]
            subPot = 0
            for i in range(self._s['numP']):
                contribution = min(minLiveBet, self._s['bets'][i])
                self._s['bets'][i] -= contribution
                subPot += contribution


            #pay winners
            winnings = int(float(subPot) / len(winners))
            for w in winners:
                w.addChips(winnings)
                subPot -= winnings
                if self._vocal:
                    if minRank == -1:    #everyone else folded
                        print w.getName(), 'wins', winnings
                    else:   
                        if n == 0: print w.getName(), 'wins', winnings, 'from main pot'
                        if n > 0: print w.getName(), 'wins', winnings, 'from side pot'

            #give odd chips to player in earliest position
            if subPot > 0:
                actor = (self._dealer + 1) % self._s['numP']
                while subPot > 0:
                    player = self._playing[actor]
                    if player in winners:
                        player.addChips(subPot)
                        if self._vocal: print player.getName(), 'wins', subPot, 'odd chips'
                        subPot = 0
                    actor = (actor + 1) % self._s['numP']

            n += 1

    def _openBetting(self): 

        """ The method starts a round of betting. """

        lastRaiser = self._s['actor']    #so that action ends when everyone checks

        #main betting loop
        t = 0
        while True: 
            t += 1      

            actor = self._s['actor']

            if actor == lastRaiser and t > 1: break    #break if last raising player has been reached
            
            #break if no further calls are possible
            notAllinOrFold = []
            for i in range(self._s['numP']):
                if i not in self._s['folded'] and i not in self._s['allIn']: notAllinOrFold.append(i)
            if len(notAllinOrFold) == 0: break    #break if all players are folded or all-in
            #break if last player's raise cannot be matched
            if len(notAllinOrFold) == 1 and self._s['currBets'][notAllinOrFold[0]] == max(self._s['currBets']): break    

            #skip player if player folded or player is all in
            if actor in self._s['folded'] or actor in self._s['allIn']: 
                self._s['actor'] = (actor + 1) % self._s['numP'] 
                continue

            self._s['toCall'] = max(self._s['currBets']) - self._s['currBets'][actor]    #player must call maximum bet to call

            #request player action and parse action
            action = self._playing[actor].act(self._s)
            self._parseAction(action)
            if action[0] == 'raise': lastRaiser = actor
            
            self._s['actor'] = (actor + 1) % self._s['numP']  #move to next player

        #return uncalled chips to raiser
        uniqueBets = sorted(set(self._s['currBets']))
        maxBet = uniqueBets[-1]
        if len(uniqueBets) >= 2: belowMax = uniqueBets[-2]
        if len([b for b in self._s['currBets'] if b==maxBet]) == 1:
            for i in range(self._s['numP']):
                if self._s['currBets'][i] == maxBet:
                    self._s['currBets'][i] = belowMax
                    player = self._playing[i]
                    player.addChips(maxBet - belowMax)
                    if self._vocal: print maxBet - belowMax, 'uncalled chips return to', player.getName() 

        self._s['actor'] = None    #action has closed
        
        #add bets of current round to bets and flush currBets and numRaises
        for i in range(len(self._s['currBets'])): 
            self._s['bets'][i] += self._s['currBets'][i]    
            self._s['currBets'][i] = 0
            self._s['numRaises'][i] = 0

    def _parseAction(self, action):

        """ 
        This method accepts a tuple of the form (action string, amount) or (action string,) and changes
        the game state, self._s, appropriately.
        """
        actor = self._s['actor']
        player = self._playing[actor]
        m = max(self._s['currBets'])    #largest contribution that any player has in current pot
        currentBet = self._s['currBets'][actor]

        if action[0] == 'check':
            if currentBet < m: raise Exception('Player must call to remain in the pot.')
            if self._vocal: print player.getName(), 'checks.'
        
        elif action[0] == 'fold': 
            self._s['folded'].append(actor)
            if self._vocal: print player.getName(), 'folds.'  
        
        elif action[0] == 'call': 
            toCall = self._s['toCall']
            if toCall == 0: raise Exception('Player called a bet of 0 chips. Did you mean to check?')
            stack = player.getStack()
            if stack <= toCall:    #player has all-in called
                self._s['currBets'][actor] += stack
                player.removeChips(stack)
                if self._vocal: print player.getName(), 'all-in calls with', stack 
                self._s['allIn'].append(actor)
            else:
                self._s['currBets'][actor] = m
                player.removeChips(m - currentBet)
                if self._vocal: print player.getName(), 'calls', m - currentBet
        
        elif action[0] == 'raise' or action[0] == 'bet':    #raising is interpreted as "raise to" a a new total bet
            raiseTo = action[1]    #new total bet of player
            raiseBy = raiseTo - m    #change in maximum bet in pot
            # if action[0] == 'bet' and m > 0: raise Exception('Cannot bet when pot has been opened. Did you mean to raise?')
            # if action[0] == 'raise' and m == 0: raise Exception('Cannot raise when pot is unopened. Did you mean to bet?')
            if raiseTo < self._s['minRaise']: raise Exception('Raise amount is less than minimum raise.')
            self._s['minRaise'] = raiseTo + raiseBy    #player must raise by twice as much as last raise
            self._s['currBets'][actor] = raiseTo
            player.removeChips(raiseTo - currentBet)
            self._s['numRaises'][actor] += 1
            allIn  = player.getStack() == 0
            if allIn: self._s['allIn'].append(actor)
            if self._vocal: 
                if not allIn: print player.getName(), 'raises', raiseBy, 'to', raiseTo
                else: print player.getName(), 'raises all-in', raiseBy, 'to', raiseTo
        
        else: raise Exception('Invalid player action.')

    def getPlaying(self): return self._playing[:]

    def getSitOut(self): return self._sitOut[:]

    def getPlayers(self): return self._players[:]

    def getParams(self): return (self._smallBlind, self._bigBlind, self._maxBuyIn)
