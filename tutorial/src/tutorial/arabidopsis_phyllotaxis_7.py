# coding; O: alpha | 1: 2 alpha | 2: -alpha | 3: 3 alpha | 4: -2 alpha | 5: 4 alpha | 6: 5 alpha.

def state(alpha):
    return [alpha, 2*alpha, -alpha, 3*alpha, -2*alpha, 4*alpha, 5*alpha]

# MARKOV_CHAIN

# 7 STATES

# TRANSITION_PROBABILITIES                             memory

transition_probability =\
[[1,     0,     0,     0,     0,     0,     0],     #  0:            initial
 [0.88,  0.09,  0,     0.01,  0.01,  0.01,  0],     #  1:    0       terminal
 [0,     1,     0,     0,     0,     0,     0],     #  2:    1   non-terminal (not used)
 [0.1,   0.01,  0.88,  0.01,  0,     0,     0],     #  3:  0 1       terminal
 [0.07,  0,     0.93,  0,     0,     0,     0],     #  4:  1 1       terminal
 [0.81,  0.18,  0,     0.01,  0,     0,     0],     #  5:  2 1       terminal
 [0.99,  0,     0.01,  0,     0,     0,     0],     #  6:  3 1       terminal
 [0,     0,     0,     0,     1,     0,     0],     #  7:  4 1       terminal (not used)
 [0,     0,     0,     0,     0,     1,     0],     #  8:  5 1       terminal (not used)
 [0,     0,     0,     0,     0,     0,     1],     #  9:  6 1       terminal (not used)
 [0,     0.7,   0.08,  0.19,  0,     0.02,  0.01],  # 10:    2       terminal
 [0.27,  0.03,  0.54,  0.05,  0.11,  0,     0],     # 11:    3       terminal
 [0.3,   0,     0,     0.4,   0,     0.2,   0.1],   # 12:    4       terminal
 [0.2,   0,     0.6,   0,     0.2,   0,     0],     # 13:    5       terminal
 [0,     0,     0.5,   0,     0.5,   0,     0]]     # 14:    6       terminal

# memory transition matrix

memory_transition =\
[[1, 2, 10, 11, 12, 13, 14],  #  0: init  =>  0     1   2   3   4   5   6       initial
 [1, 3, 10, 11, 12, 13, 14],  #  1:    0  =>  0   0 1   2   3   4   5   6       terminal
 [1, 4, 10, 11, 12, 13, 14],  #  2:    1  =>  0   1 1   2   3   4   5   6   non-terminal
 [1, 4, 10, 11, 12, 13, 14],  #  3:  0 1  =>  0   1 1   2   3   4   5   6       terminal
 [1, 4, 10, 11, 12, 13, 14],  #  4:  1 1  =>  0   1 1   2   3   4   5   6       terminal
 [1, 4, 10, 11, 12, 13, 14],  #  5:  2 1  =>  0   1 1   2   3   4   5   6       terminal
 [1, 4, 10, 11, 12, 13, 14],  #  6:  3 1  =>  0   1 1   2   3   4   5   6       terminal
 [1, 4, 10, 11, 12, 13, 14],  #  7:  4 1  =>  0   1 1   2   3   4   5   6       terminal
 [1, 4, 10, 11, 12, 13, 14],  #  8:  5 1  =>  0   1 1   2   3   4   5   6       terminal
 [1, 4, 10, 11, 12, 13, 14],  #  9:  6 1  =>  0   1 1   2   3   4   5   6       terminal
 [1, 5, 10, 11, 12, 13, 14],  # 10:    2  =>  0   2 1   2   3   4   5   6       terminal
 [1, 6, 10, 11, 12, 13, 14],  # 11:    3  =>  0   3 1   2   3   4   5   6       terminal
 [1, 7, 10, 11, 12, 13, 14],  # 12:    4  =>  0   4 1   2   3   4   5   6       terminal
 [1, 8, 10, 11, 12, 13, 14],  # 13:    3  =>  0   3 1   2   3   4   5   6       terminal
 [1, 9, 10, 11, 12, 13, 14]]  # 14:    4  =>  0   4 1   2   3   4   5   6       terminal

# recurrent class: states 0 1 2 3 4

# memory tree

# |___0
# |___1___0 1
# |   |___1 1
# |   |___2 1
# |   |___3 1
# |   |___4 1
# |   |___5 1
# |   |___6 1
# |___2
# |___3
# |___4
# |___4
# |___5
