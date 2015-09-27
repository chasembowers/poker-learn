import random
from sklearn.ensemble import RandomForestRegressor
import numpy as np

class Player:

    """
    This class keeps a player's current stack size and bankroll and is primarily responsible for
    receiving gameStates and returning actions.
    """

    def __init__(self, name, bankroll, rChoices, memory):
        
        self._bankroll = bankroll    #total wealth of player
        self._stack = 0              #chips that player has on table
        self._name = name            #for distinction from other players
        self._features = []          #features associated with each gameState seen
        self._stacks = []            #stack size at each time that features are recorded
        self._labels = []            #result of each hand played
        self._regressor = None       #machine learning regressor which predicts return on action
        self._rChoices = rChoices    #number of discrete choices player considers for raising
        self._memory = memory        #max number of features, stacks, and labels to store

        self._enum = {'fold':0, 'check':1, 'call':2, 'raise':3, 'bet':4}

    def getName(self): return self._name

    def buyIn(self, minBuyIn, maxBuyIn):

        """
        This method accepts the minimum and maximum amount of chips to buy in at a table and returns
        True if the player has enough chips to play.
        """

        if minBuyIn > self._bankroll + self._stack: return False    #player has gone bankrupt

        if self._stack >= maxBuyIn: 
            self._startingStack = self._stack
            return True

        newStack = min(maxBuyIn, self._bankroll + self._stack)
        move = newStack - self._stack
        self._bankroll -= move
        self._stack += move
        return True

    def cashOut(self):
        self._bankroll += self._stack
        self._stack = 0

    def act(self, gameState):

        """ 
        Accepts a gameState object and returns an action in the form (action_string, amount). 
        Valid action_strings are fold, check, call, raise, and bet.
        """

        gameFeatures = self._genGameFeatures(gameState)
        allActions = self._allActions(gameState)  

        #if player has not yet been trained
        if not self._regressor: 
            action = random.choice(allActions)    #take a random action
            actionFeatures = self._genActionFeatures(action, gameState)  
            self._features.append(gameFeatures + actionFeatures)
            self._stacks.append(self._stack)
            return action      

        else:
            allFeatures = []
            for a in allActions: allFeatures.append(gameFeatures + self._genActionFeatures(a, gameState))
            pReturn = self._regressor.predict(allFeatures)
            action = allActions[np.argmax(pReturn)]

            actionFeatures = self._genActionFeatures(action, gameState)  
            self._features.append(gameFeatures + actionFeatures)
            self._stacks.append(self._stack)
            return action      

    def removeChips(self, amt):
        if amt > self._stack: raise Exception('Requested chips is greater than stack size.')
        if type(amt) != int: raise Exception('Must remove integer number of chips.')
        self._stack -= amt

    def addChips(self, amt): 
        if type(amt) != int: raise Exception('Must add integer number of chips.')
        self._stack += amt

    def postBlind(self, blind):

        self._stack -= blind
        return blind

    def takeHoleCards(self, cards): self._cards = cards

    def show(self): return self._cards

    def getStack(self): return self._stack

    def endHand(self): 

        """
        This method discards data older than 'self._memory' and updates 'self._labels' with 
        the change from stack size at each feature generation.
        """

        self._features = self._features[-self._memory:]
        self._stacks = self._stacks[-self._memory:]
        self._labels = self._labels[-self._memory:]

        self._labels = self._stack - np.array(self._stacks)

    def train(self):

        """ 
        This method trains the player's regressor using the set of gathered features and labels
        in ordered to predict the outcome of any given action.
        """

        self._regressor = RandomForestRegressor()

        self._regressor.fit(self._features, self._labels)

    def _allActions(self, gameState):
        
        """ This method accepts the dictionary gameState and returns the set of all possible actions. """

        toCall = gameState['toCall']    #amount necessary to call
        minRaise = gameState['minRaise']    #new total bet amount necessary to raise
        currentBets = gameState['currBets']
        myCurrentBet = currentBets[gameState['actor']]
        maxBet = self._stack + myCurrentBet    #maximum bet player could have in pot, including chips already in pot

        actions = []    #set of all possible actions

        if toCall >= self._stack:   #player does not have enough chips to call without all-in
            actions.append(('call',))
            actions.append(('fold',))
            
        elif maxBet >= minRaise:    #player has enough chips to raise

            #generate logrithmically distributed integer raises
            start = np.log10(minRaise)
            end = np.log10(maxBet)
            for r in np.logspace(start, end, self._rChoices): actions.append(('raise', int(r + .5)))
            
            if toCall == 0: actions.append(('check',))
            else: 
                actions.append(('call',))
                actions.append(('fold',))
        
        else:    #player only has enough chips to call or check
            if toCall == 0: actions.append(('check',))
            else: 
                actions.append(('call',))
                actions.append(('fold',))

        return actions

    def _genGameFeatures(self, gameState):

        """ 
        This method generates a set of features from a gameState and independently of the
        action a player takes. 
        """

        gameFeatures = 26 * [0]

        holeCards = sorted(self._cards)
        tableCards = sorted(gameState['cards'])

        cards = holeCards + tableCards
        for i in range(len(cards)):
            gameFeatures[2 * i] = cards[i].getNumber()
            gameFeatures[2 * i + 1] = cards[i].getSuit(num=True)

        me = gameState['actor']
        numP = gameState['numP']
        for i in range(numP):
            gameFeatures[i* 2 + 14] = gameState['bets'][(i - me)%numP]
            gameFeatures[i* 2 + 15] = gameState['currBets'][(i - me)%numP]

        return gameFeatures

    def _genActionFeatures(self, action, gameState):

        """ This method generates a set of features from a player action. """

        actionFeatures = 3 * [0]

        actionFeatures[0] = self._enum[action[0]]
        if len(action) == 2: 
            actionFeatures[1] = action[1]
            actionFeatures[2] = float(action[1]) / sum(gameState['bets'] + gameState['currBets'])    #proportion of raise to pot size

        return actionFeatures