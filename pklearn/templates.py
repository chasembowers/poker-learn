import time
from player import Player

def simulate(table, nHands, firstTrain=0, nTrain=0, nBuyIn=0, tPrint=5, vocal=False):  

    """
    This function simulates several hands of Holdem according to these parameters:

    Parameters:
    table - table used in simulation (Table)
    nHands - total number of hands to simulate (int)
    firstTrain - number of hands before first training, when players take random actions (int)
    nTrain - number of hands between training players (int)
    nBuyIn - number of hands between cashing out/buying in players (int)
    tPrint - number of seconds between printing hand number (int)
    vocal - hands are narrated by table when vocal is True (bool)
    """

    print 'Beginning simulation of', nHands, 'hands.'

    players = table.getPlayers()
    bankroll = [[] for p in players]    #holds bankroll history of all players
    maxBuyIn = table.getParams()[-1]

    #set Player stack sizes to max buy-in or less
    for p in players: 
        p.cashOut()
        if p.getStack() < maxBuyIn: p.buyChips(maxBuyIn)

    nextTrain = firstTrain    #next hand players will train
    if firstTrain == 0: nextTrain = nTrain
    nextBuyIn = nBuyIn        #next hand players will cash out and buy in
    hand = 1                  #hands started
    lastTime = time.time()    #last time printed hands completed
    while hand <= nHands:

        if time.time() - lastTime > tPrint:
            lastTime = time.time()
            print hand - 1, 'hands simulated.'
        
        if hand == nextTrain:
            print 'Players are training...'
            for p in players: p.train()
            nextTrain = hand + nTrain
            print 'Complete.'

        if hand == nextBuyIn:
            if vocal: print 'Players are cashing out and buying in.'
            for p in players:
                p.cashOut()
                if p.getStack() < maxBuyIn: p.buyChips(maxBuyIn)
            nextBuyIn = hand + nBuyIn

        if vocal: print 'Hand', hand
        played = table.playHand(vocal=vocal)
        
        #Hand failure
        if not played:    
            if nextBuyIn == hand + nBuyIn:    #if players just bought in
                print 'All or all but one players are bankrupt.'
                break

            #buy in and redo hand
            if vocal: print 'Not enough eligible players.'
            nextBuyIn = hand    
            hand -= 1
        
        hand += 1

        for i in range(len(players)): bankroll[i].append(players[i].getBankroll())

    print 'Simulation complete.\n'
    return bankroll

class BasicPlayer(Player):

    def _genGameFeatures(self, gameState):

        """ 
        This method generates a set of features from a gameState and independently of the
        action a player takes. 
        """

        gameFeatures = 43 * [0]

        holeCards = sorted(self._cards)
        tableCards = sorted(gameState.cards)

        #add number and suit of each card to features
        cards = holeCards + tableCards
        for i in range(len(cards)):
            gameFeatures[6 * i] = 1    #ith card exists
            gameFeatures[6 * i + 1] = cards[i].getNumber()
            suit = cards[i].getSuit()
            
            #create binary encoding for suit
            gameFeatures[6 * i + 2] = suit == 'c' 
            gameFeatures[6 * i + 3] = suit == 'd'
            gameFeatures[6 * i + 4] = suit == 's'
            gameFeatures[6 * i + 5] = suit == 'h'

        #player stack size
        gameFeatures[42] = self._stack

        return gameFeatures

    def _genActionFeatures(self, action, gameState):

        """ This method generates a set of features from a player action. """

        #create binary encoding for action type
        actionFeatures = 7 * [0]

        if action[0] == 'check': actionFeatures[0] = 1
        elif action[0] == 'fold': actionFeatures[1] = 1
        elif action[0] == 'call': actionFeatures[2] = 1
        elif action[0] == 'raise' or action[0] == 'bet':
            actionFeatures[3] = 1
            actionFeatures[4] = action[1]    #raise to amount
            actionFeatures[5] = action[1] - max(gameState.currBets)    #raise by amount
            actionFeatures[6] = actionFeatures[5] / sum(gameState.bets + gameState.currBets)    #proportion of raise by to pot size
        else: raise Exception('Invalid action.')

        return actionFeatures