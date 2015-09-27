from table import Table
from player import Player
import numpy as np

if __name__ == '__main__':
    
    t = Table(1,2,200)
    players = []

    for i in range(6):
        p = Player('Player ' + str(i+1), np.inf, 10, 100000)
        players.append(p)
    
    for p in players: t.addPlayer(p) 
    t.play(1000, 10, vocal=False)

    t.play(10, 1, vocal=True)    
