pklearn
========

Machine Learning in No Limit Texas Holdem

## Description

This is a small library which allows for the simulation of No Limit Texas Holdem between autonomous players
which are built around machine learning models.  pklearn is made specifically for use with the scikit-learn
machine learning library, although any regressor which implements 'fit' and 'predict' methods will work. 
Fundamentally, this library consists of the Table object simulating a hand by sending game states and requesting
 actions from its Player objects.  Before the first round of learning, players choose a random action.  Several
 demo files are included.

In the simplest case, players are trained, and then test hands are narrated:

narration_demo.py
```python
t = Table(smallBlind=1, bigBlind=2, maxBuyIn=200)

players = []
for i in range(6):
    
    #create Player that uses GradientBoostingRegressor as machine learning model
    #with wealth of 1 million and 10 discrete choices for raising,
    #with each raise choice .7 times the next largest raise choice
    #Player forgets training samples older than 100,000
    r = GradientBoostingRegressor()
    name = 'Player ' + str(i+1)
    p = Player(name=name, reg=r, bankroll=10**6, nRaises=10, rFactor=.7, memory=10**5)
    players.append(p)

for p in players: t.addPlayer(p)

#simulate 'nHands' hands
#begin training after 'firstTrain' hands
#before which players take random actions and explore state space
#players train every 'nTrain' hands after 'firstTrain'
#players cash out/ buy in every 'nBuyIn' hands
#table narrates each hands if 'vocal' is True
simulate(t, nHands=10000, firstTrain=2000, nTrain=1000, nBuyIn=10)
simulate(t, nHands=20, nBuyIn=10, vocal=True)
```

    Hand 5
    Player 2(1141) dealt 8d and Qs
    Player 4(59) dealt 6c and As

    Player 2 posts small blind of 1
    Player 4 posts big blind of 2
    Player 2 calls 1
    Player 4 raises 11 to 13
    Player 2 calls 11

    ['3h', 'Kc', '5c']
    Player 4 checks.
    Player 2 raises 270 to 270
    Player 4 all-in calls with 46
    224 uncalled chips return to Player 2

    ['3h', 'Kc', '5c', 'Qd']

    ['3h', 'Kc', '5c', 'Qd', '8s']

    Player 2 wins 118 from main pot

Players that are trained more have a tendency to be more skilled:

bankroll_demo.py
```python
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
plt.legend(loc='upper left')
plt.show()
```
Player 2's bankroll reflects that it has seen 10,000 more hands than Player 1. 
![alt tag](https://raw.githubusercontent.com/chasembowers/pklearn/master/bankroll.png)

For the purpose of testing different regressors, a demo file is included which cross_validates
several regressors with features and labels taken from Players.

cross_val_demo.py
```python
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
```

## Simplifications

Some simplifications are made. For example, the set of all possible raises is reduced to a smaller set. This 
decreases the number of actions for which a Player must predict return and, as a result, decreases computational
load. Specific raise amounts are chosen to represent a logrithmic distribution over a Player's stack.  The intuition behind
 this decision is that a player is exponentially less likely to choose linearly greater raise amounts. In addition, Players
play with integer amounts of chips of uniform value, and there is no distinction made between betting and raising.

Most interestingly, players attempt to maximize the expected value of the return on any particular action.
The prefered alternative would be that Players maximize their own uility. That is, that the players are risk-
averse.  Because risk-aversion has not been implemented, players are prone to taking wildly large bets.  I plan to
address this in the future.  Finally, some of the more intricate Holdem rules are excluded.

## Features and Labels

Each time a player receives a game state, the player generates a set of features corresponding to that game state 
and and the action the player has chosen. At present, these generated features are very simplistic.  They include
the number and suit of hole cards and community cards and the Player's stack. These features are stored and later associated
 with a label.  The label is calculated at the end of each hand and is the difference between the player's stack at the end 
 of the hand and the player stack size at the moment of the action.  Categorical features are represented with a binary encoding.
Custom features can be generated by creating a sub-class of Player and implementing '_genGameFeatures' and '_genActionFeatures'.
This will be better supported in the future.

After each iteration, the player is trained using a fixed amount of features and labels.  The remainder of features and
labels from the beginning of the player's career are discarded. The reason for discarding is that the expected return of a
Player's action  is a function of the Player's future actions in any hand, so older samples become inaccurate as a Player evolves. 
A machine learning regressor is used to approximate a function from the set of stored features to the set of stored labels. In order to
 predict the best action, the player evaluates this function for its received game state and over the entire set of possible actions.
 The action which is evaluated to the maximum expected value of return is chosen.

Before Player's have been trained, they take random actions with the purpose of gathering features and labels associated with random
game states.  I have observed that when this period contains few hands, when Players do not sufficiently explore the state space,
it can lead to some strange and upredictable behavior

## Machine Learning Models

After experimenting with various machine learning models,  I have had most success with linear models and ensemble models.
I suspect that this is because both are resistant to overfitting the large amount of randomness that is present in poker.
 Ensemble models work by fitting regressors to multiple random subsets of the training data.  In this way, they minimize overfitting
while linear models avoid overfitting via their simplicity.  Ensemble methods seem to outperform linear methods.  This is likely
because ensemble methods can capture the nonlinearities present in Holdem with regressors like decision trees.  As for specific
models, best performance was observed with GradientBoostingRegressor.  Linear models performed well and quickly, and support vector
machines took far too long to train.

## External Packages

sklearn - library which implements machine learning models

numpy - array manipulation library, dependency for sklearn

deuces - package which evaluates rank of poker hands, included in this project

matplotlib - graphing library, necessary for running demo

## License

The MIT License (MIT)

Copyright (c) 2015 Chase M Bowers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
