from table import Table
from player import Player
import numpy as np

if __name__ == '__main__':
    
    t = Table(smallBlind=1, bigBlind=2, maxBuyIn=200)
    
    players = []
    for i in range(6):
        #create Player with infinite bankroll, 10 choices for raising, and a maximum of 100,000 training samples
        p = Player(name='Player ' + str(i+1), bankroll=np.inf, rChoices=10, memory=100000)
        players.append(p)
    
    for p in players: t.addPlayer(p) 

    #Simulate 10 iterations of 1000 hands
    t.play(maxHands=1000, iters=2, vocal=False)
    
    #Simulate 5 hands and narrate the hands
    t.play(maxHands=5, iters=1, vocal=True)