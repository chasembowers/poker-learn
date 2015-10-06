import time

def simulate(table, nHands, firstTrain=0, nTrain=0, nBuyIn=0, tPrint=5, vocal=False):  

    """
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
    bankroll = [[] for p in players]
    maxBuyIn = table.getParams()[-1]

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
        
        if not played:    
            if nextBuyIn == hand + nBuyIn:    #if players just bought in
                print 'All or all but one players are bankrupt.'
                break
            if vocal: print 'Not enough eligible players.'
            #buy in and redo hand
            nextBuyIn = hand    
            hand -= 1
        
        hand += 1

        for i in range(len(players)): bankroll[i].append(players[i].getBankroll())

    print 'Simulation complete.\n'
    return bankroll