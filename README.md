Machine Learning  in Texas Holdem
========

Experimental project in which No Limit Texas Holdem players evolve using machine learning

## Description

This project is a rough prototype of a No Limit Texas Holdem Simulator, which involves players who learn iteratively
using machine learning.  Fundamentally, the simulation consists of the Table object requesting actions from the
Player object.  The player returns an action from the set of all possible actions. Before the first round of learning, 
players choose a random action.  'main.py' contains an example of basic usage.

```python
t = Table(smallBlind=1, bigBlind=2, maxBuyIn=200)

players = []
for i in range(6):
    #create Player with infinite bankroll, 10 choices for raising, and a maximum of 100,000 training samples
    p = Player(name='Player ' + str(i+1), bankroll=np.inf, rChoices=10, memory=100000)
    players.append(p)

for p in players: t.addPlayer(p) 

#Simulate 10 iterations of 1000 hands
t.play(maxHands=1000, iters=10, vocal=False)

#Simulate 5 hands and narrate the hands
t.play(maxHands=5, iters=1, vocal=True)
```

## Simplifications

Some simplifications are made. For example, the set of all possible raises is reduced to a smaller set.  
Logrithmically distributed amounts from the range of possible raise amounts are chosen.  This simplification is made
for the purpose of speed.  In addition, players play with integer amounts of chips of uniform value.

Most interestingly, players attempt to maximize the expected value of the return on any particular action.
The preffered alternative would be that the players maximize their own uility. That is, that the players are risk-
averse.  Because risk-aversion has not been implemented, players are prone to taking wildly large bets.  I plan to
address this in the future.  Finally, some of the more intricate Holdem rules are excluded.

## Features and Labels

Each time a player receives a game state, the player generates a set of features corresponding to that game state 
and and the action the player has chosen. As this is a prototype, these generated features are simplistic.  They include
the number and suit of hole cards and community cards, the position of the player, and the size of each player's total
contribution to the pot. These features are stored and later associated with a label.  The label is calculated at the 
end of each hand and is the difference between the player's stack at the end of the hand and the player stack size at 
the moment of the action.

After each round, the player is trained using a fixed amount of features and labels.  The remainder of features and
labels from the beginning of the player's career are discarded. This is implemented because the expected return of a
player's action will change as a player evolves.  A machine learning regressor is used to approximate a function from
the set of stored features to the set of stored labels. In order to predict the best action, the player evaluates this
function for its received game state and over the entire set of possible actions. The action which is evaluated to the
maximum expected value of return is chosen.

## Machine Learning Models

After experimenting with various sophisticated machine learning models like support vector machines and random forests, I 
have only had success with a simple multiple regression model. I suspect that this is because the sample space is 
extremely noise; poker involves a lot of luck, and simpler models are more resistant to overfitting.

## External Packages

sklearn - library which implements machine learning models

deuces - package which evaluates rank of poker hands, included in this project

## Examples

Training

```python
**********************************************
           1/2 No Limit Holdem             
**********************************************
Maximum hands: 1000
Iterations: 10
 
Beginning iteration 1 ...
(Untrained players are taking random actions.)
Complete. Training players ...
Training complete.

Beginning iteration 2 ...
351 hands simulated.
786 hands simulated.
Complete. Training players ...
Training complete.
```

Playing

```python
Hand 5
Player 1 dealt 7d and 9d
Player 2 dealt Jc and 7c
Player 3 dealt 8h and Jh
Player 4 dealt As and Qs
Player 5 dealt 9c and Jd
Player 6 dealt 6d and 5h

Player 4 posts small blind of 1
Player 5 posts big blind of 2
Player 6 folds.
Player 1 folds.
Player 2 raises 2 to 4
Player 3 raises all-in 396 to 400
Player 4 all-in calls with 199
Player 5 all-in calls with 198
Player 2 folds.
200 uncalled chips return to Player 3

['Qd', '6h', '8d']

['Qd', '6h', '8d', '4h']

['Qd', '6h', '8d', '4h', 'Tc']

Player 5 wins 604 from main pot
```

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
