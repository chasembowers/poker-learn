import random
import numpy as np
from sklearn.linear_model import LinearRegression

class Player:

    """
    This class keeps a player's current stack size and bankroll and is primarily responsible for
    receiving gameStates and returning actions.
    """

    def __init__(self, name, bankroll, nRaises, memory, rFactor=None, reg=None):

        """ 
        Parameters

        name - player's name (string)
        bankroll- player's net worth (int)
        nRaises - number of raise choices player has, all-in always included (int)
        memory - player forgets oldest stored features/labels that exceed memory in quantity (int)
        rFactor - each raise choice is rFactor times the next largest raise choice (float)
        """
        
        self._name = name            #for distinction from other players
        self._fit = False            #True when self._reg has been fit
        self._bankroll = bankroll    #total wealth of player
        self._stack = 0              #chips that player has on table
        self._features = []          #features associated with each gameState seen
        self._stacks = []            #stack size at each time that features are recorded
        self._labels = []            #result of each hand played
        self._memory = memory        #max number of features, stacks, and labels to store
        self._reg = reg              #machine learning regressor which predicts return on action
        
        self._train = True           #player will not update regressor if self._train is False

        if rFactor == None and nRaises != 1:
            raise Exception('Must set \'rFactor\' when \'nRaises\ is not 1.')
        if rFactor <= 0 or rFactor >= 1: raise Exception('rFActor must be between 0 and 1, exclusive.')

        #generate logrithmically distributed raise choices, as multiples of stack
        self._rChoices = [1]
        for i in range(nRaises - 1):
            self._rChoices = [self._rChoices[0] * rFactor] + self._rChoices

    def buyChips(self, newStack):

        """ This method moves chips to player's bankroll such that player's stack is 'newStack'. """

        if newStack > self._bankroll + self._stack: return False    #player cannot buy chips

        if newStack < self._stack: raise Exception('Requested stack is smaller than old stack.')

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
        if not self._fit: action = random.choice(allActions)    #take a random action

        else:
            #determine best action
            allFeatures = []
            for a in allActions: allFeatures.append(gameFeatures + self._genActionFeatures(a, gameState))
            pReturn = self._reg.predict(allFeatures)
            action = allActions[np.argmax(pReturn)]

        #store action features
        actionFeatures = self._genActionFeatures(action, gameState)  

        if self._train: 
            self._stacks.append(self._stack)
            self._features.append(gameFeatures + actionFeatures)
        return action      

    def removeChips(self, amt):
        if amt > self._stack: raise Exception('Requested chips is greater than stack size.')
        if type(amt) != int: raise Exception('Must remove integer number of chips.')
        self._stack -= amt

    def addChips(self, amt): 
        if type(amt) != int: raise Exception('Must add integer number of chips.')
        self._stack += amt

    def endHand(self): 

        """
        This method discards data older than 'self._memory' and updates 'self._labels' with 
        the change from stack size at each feature generation.
        """

        for i in range(len(self._labels), len(self._features)):
            self._labels.append(self._stack - self._stacks[i])

        self._features = self._features[-self._memory:]
        self._stacks = self._stacks[-self._memory:]
        self._labels = self._labels[-self._memory:]

    def train(self):

        """ 
        This method trains the player's regressor using the set of gathered features and labels
        in ordered to predict the outcome of any given action.
        """
        
        if not self._train: return

        self._reg.fit(self._features, self._labels)
        self._fit = True

    def _allActions(self, gameState):
        
        """ This method accepts the dictionary gameState and returns the set of all possible actions. """

        toCall = gameState['toCall']    #amount necessary to call
        minRaise = gameState['minRaise']    #new total bet amount necessary to raise
        currentBets = gameState['currBets']
        myCurrentBet = currentBets[gameState['actor']]
        maxBet = self._stack + myCurrentBet    #maximum bet player could have in pot, including chips already in pot

        actions = []    #set of all possible actions

        if toCall > self._stack:   #player cannot match entire bet
            actions.append(('call',))
            actions.append(('fold',))
            return actions
            
        if maxBet < minRaise:    #player has enough chips to call but not to raise
            if toCall == 0: actions.append(('check',))
            else: 
                actions.append(('call',))
                actions.append(('fold',))
            return actions

        #add eligible raise choices to actions
        #raise actions include a raise to amount, not a raise by amount
        for r in self._rChoices:
            amt = int(self._stack * r) 
            if amt >= minRaise and amt <= maxBet: actions.append(('raise', amt))

        #player has enough chips to raise
        if toCall == 0: actions.append(('check',))
        else:
            actions.append(('call',))
            actions.append(('fold',))
        
        return actions

    def _genGameFeatures(self, gameState): raise Exception('This method must be implemented in an inherited class.')

    def _genActionFeatures(self, action, gameState): raise Exception('This method must be implemented in an inherited class.')

    def takeHoleCards(self, cards): self._cards = cards

    def stopTraining(self): self._train = False

    def startTraining(self): self._train = True

    def show(self): return self._cards

    def getStack(self): return self._stack

    def getBankroll(self): return self._bankroll

    def getName(self): return self._name

    def getRaiseChoices(self): return self._rChoices[:]

    def getFeatures(self): return self._features[:]

    def getLabels(self): return self._labels[:]

    def setBankroll(self, amt): self._bankroll = amt