# coding; O: alpha | 1: 2 alpha | 2: -alpha | 3: 3 alpha | 4: -2 alpha.

def state(alpha):
    return [alpha, 2*alpha, -alpha, 3*alpha, -2*alpha]

# MARKOV_CHAIN

# 5 STATES

# TRANSITION_PROBABILITIES           memory

transition_probability = \
[[1,    0,    0,    0,    0],     #  0:            initial
 [0.89, 0.09, 0,    0.01, 0.01],  #  1:    0       terminal
 [0,    1,    0,    0,    0],     #  2:    1   non-terminal  (not used)
 [0.08, 0,    0.91, 0.01, 0],     #  3:  0 1       terminal
 [0.06, 0,    0.94, 0,    0],     #  4:  1 1       terminal
 [0.81, 0.18, 0,    0.01, 0],     #  5:  2 1       terminal
 [0.01, 0,    0,    0.36, 0.63],  #  6:  3 1       terminal
 [0.67, 0.08, 0.25, 0,    0],     #  7:  4 1       terminal
 [0.01, 0.72, 0.07, 0.18, 0.02],  #  8:    2       terminal
 [0.19, 0.01, 0.63, 0.03, 0.14],  #  9:    3       terminal
 [0.25, 0.16, 0.05, 0.13, 0.41]]  # 10:    4       terminal

# memory transition matrix

memory_transition = \
[[1, 2, 8, 9, 10],  #  0: init  =>  0     1   2   3   4       initial
 [1, 3, 8, 9, 10],  #  1:    0  =>  0   0 1   2   3   4       terminal
 [1, 4, 8, 9, 10],  #  2:    1  =>  0   1 1   2   3   4   non-terminal
 [1, 4, 8, 9, 10],  #  3:  0 1  =>  0   1 1   2   3   4       terminal
 [1, 4, 8, 9, 10],  #  4:  1 1  =>  0   1 1   2   3   4       terminal
 [1, 4, 8, 9, 10],  #  5:  2 1  =>  0   1 1   2   3   4       terminal
 [1, 4, 8, 9, 10],  #  6:  3 1  =>  0   1 1   2   3   4       terminal
 [1, 4, 8, 9, 10],  #  7:  4 1  =>  0   1 1   2   3   4       terminal
 [1, 5, 8, 9, 10],  #  8:    2  =>  0   2 1   2   3   4       terminal
 [1, 6, 8, 9, 10],  #  9:    3  =>  0   3 1   2   3   4       terminal
 [1, 7, 8, 9, 10]]  # 10:    4  =>  0   4 1   2   3   4       terminal

# recurrent class: states 0 1 2 3 4

# memory tree

# |___0
# |___1___0 1
# |   |___1 1
# |   |___2 1
# |   |___3 1
# |   |___4 1
# |___2
# |___3
# |___4
