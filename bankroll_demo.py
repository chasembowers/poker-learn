from pklearn import Table
from pklearn.templates import simulate, BasicPlayer
from sklearn.ensemble import GradientBoostingRegressor

if __name__ == '__main__':

    try: import matplotlib.pyplot as plt
    except: print 'Must install matplotlib to run this demo.\n'

    t = Table(smallBlind=1, bigBlind=2, maxBuyIn=200)

    players = []
    for i in range(6):
        
        #create Player that uses GradientBoostingRegressor as machine learning model
        #with wealth of 1 million and 10 discrete choices for raising,
        #with each raise choice .7 times the next largest raise choice
        #Player forgets training samples older than 100,000
        r = GradientBoostingRegressor()
        name = 'Player ' + str(i+1)
        p = BasicPlayer(name=name, bankroll=10**6, nRaises=10, rFactor=.7, memory=10**5, reg=r)
        p.stopTraining()
        players.append(p)

    for p in players: t.addPlayer(p)

    #train Player 1 for 1000 hands, training once
    players[0].startTraining()
    simulate(t, nHands=1000, nTrain=1000, nBuyIn=10)   
    players[0].stopTraining()
    
    #train Player 2 for 10000 hands, training every 1000 hands
    players[1].startTraining()
    simulate(t, nHands=10000, nTrain=1000, nBuyIn=10)   
    players[1].stopTraining()

    for p in players: p.setBankroll(10**6)

    #simulate 20,000 hands and save bankroll history
    bankrolls = simulate(t, nHands=20000, nTrain=0, nBuyIn=10)

    #plot bankroll history of each player
    for i in range(6):
        bankroll = bankrolls[i]
        plt.plot(range(len(bankroll)), bankroll, label=players[i].getName())
    plt.title('Player bankroll vs Hands played')        
    plt.xlabel('Hands played')
    plt.ylabel('Player bankroll/wealth')
    plt.legend(loc='upper left')
    plt.show()



    