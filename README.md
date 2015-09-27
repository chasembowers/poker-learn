Machine Learning  in Texas Holdem
========

Experimental project in which No Limit Texas Holdem agents evolve using machine learning

## Description

This project is a rough first draft of a No Limit Texas Holdem Simulator, which involves players who learn iteratively
using machine learning.  Fundamentally, the simulation consists of the Table object requesting actions from the
Player object.  The player calculates the set of all possible actions given the current state of the game and 
responds with an action. Before the first round of learning, players choose a random action.

Some simplifications are made. For example, the set of all possible raises is reduced to a smaller set.  
Logrithmically distributed amounts from the range of possible raise amounts are chosen.  This simplification is made
for the purpose of speed.  In addition, players play with integer amounts of chips of uniform value.

Most interestingly, players attempt to maximize the expected value of the return on any particular action.
The preffered alternative would be that the players maximize their own uility. That is, that the players are risk-
averse.  Because risk-aversion has not been implemented, players are prone to taking wildly large bets.  I plan to
address this in the future.  Finally, some of the more intricate Holdem rules are excluded.

The machine learning portion of this project is bare bones.  Players generate a set of features corresponding to
each game state that they receive and all of the actions they could take.  This feature set corresponds to a label of
the player's change in stack size from the moment of the action until the hand is completed.  Once the player is 
trained, the player predicts the expected return on the set of all possible actions and chooses the action which 
maximizes its return.  Equivalently, the player approximates a function from a set of features, generated from a 
combination of a game state and an action, to its change in stack size.  This function is approximated using a 
machine learning regressor.  I have chosen a Random Forest because of its robustness to noise (tendency not to 
overfit) and speed in training.  A Support Vector Machine was my first choice, but it proved too train to slowly.

## External Packages

sklearn - library which implements machine learning models

deuces - package which evaluates rank of poker hands, included in this project

## Examples

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
```python
Hand 2
Player 1 dealt Qh and 8c
Player 2 dealt 9h and Td
Player 3 dealt 9s and Ts
Player 4 dealt As and Kc
Player 5 dealt 9d and Qs
Player 6 dealt 3d and 6s

Player 1 posts small blind of 1
Player 2 posts big blind of 2
Player 3 raises 2 to 4
Player 4 raises 5 to 9
Player 5 raises 10 to 19
Player 6 raises 17 to 36
Player 1 raises 35 to 71
Player 2 raises 35 to 106
Player 3 raises 35 to 141
Player 4 raises 51 to 192
Player 5 calls 173
Player 6 calls 156
Player 1 folds.
Player 2 calls 86
Player 3 calls 51

['7c', '8h', 'Tc']
Player 2 raises 2 to 2
Player 3 raises 2 to 4
Player 4 raises 2 to 6
Player 5 raises all-in 2 to 8
Player 6 all-in calls with 8
Player 2 raises 317 to 325
Player 3 all-in calls with 4
Player 4 all-in calls with 2
317 uncalled chips return to Player 2

['7c', '8h', 'Tc', '5c']

['7c', '8h', 'Tc', '5c', '6c']

Player 4 wins 1071 from main pot
```

## License

Copyright (c) 2015 Chase Bowers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
