from pklearn import Table, Player
from pklearn.templates import simulate
import numpy as np

from sklearn.cross_validation import cross_val_score
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

if __name__ == '__main__':

    try: import matplotlib.pyplot as plt
    except: print 'Must install matplotlib to run this demo.\n'

    t = Table(smallBlind=1, bigBlind=2, maxBuyIn=200)

    players = []
    for i in range(6):
        
        #create Player without a machine learning model
        #with wealth of 1 million and 10 discrete choices for raising,
        #with each raise choice .7 times the next largest raise choice 
        #Player forgets training samples older than 100,000
        name = 'Player ' + str(i+1)
        p = Player(name=name, bankroll=10**6, nRaises=10, rFactor=.7, memory=10**5)
        players.append(p)

    for p in players: t.addPlayer(p)

    #simulate 1,000 hands, cashing out/buying in every 10 hands, without training or narrating
    simulate(t, nHands=1000, nBuyIn=10, nTrain=0, vocal=False)

    features = []
    labels = []

    for p in players:
        features.extend(p.getFeatures())
        labels.extend(p.getLabels())

    features = np.array(features)
    labels = np.array(labels)

    #shuffle features/labels
    index = np.arange(len(labels))
    np.random.shuffle(index)
    features = features[index]
    labels = labels[index]

    #initialize regressors with default parameters
    regressors = {LinearRegression(): 'LinearRegression', 
                  Lasso(): 'Lasso',
                  RandomForestRegressor(): 'RandomForestRegressor',
                  GradientBoostingRegressor(): 'GradientBoostingRegressor'}
    
    for r in regressors:
        print 'Cross-validating ' + regressors[r] + '...'
        print 'Rsquared:', np.mean(cross_val_score(r, features, labels))
        print