# coding; O: alpha | 1: 2 alpha | 2: -alpha | 3: 3 alpha.

def state(alpha):
    return [alpha, 2*alpha, -alpha, 3*alpha]

# MARKOV_CHAIN

# 4 STATES

# TRANSITION_PROBABILITIES memory

transition_probability = \
[[1,   0,   0,   0],    # 0:            initial
 [0.9, 0.1, 0,   0],    # 1:    0       terminal
 [0,   1,   0,   0],    # 2:    1   non-terminal  (not used)
 [0,   0,   1,   0],    # 3:  0 1       terminal
 [0,   0,   1,   0],    # 4:  1 1       terminal
 [0.8, 0.2, 0,   0],    # 5:  2 1       terminal
 [0,   1,   0,   0],    # 6:  3 1       terminal  (not possible)
 [0,   0.8, 0,   0.2],  # 7:    2       terminal
 [0,   0,   1,   0]]    # 8:    3       terminal

# memory transition matrix

memory_transition = \
[[1, 2, 7, 8],  # 0: init  =>  0     1   2   3       initial
 [1, 3, 7, 8],  # 1:    0  =>  0   0 1   2   3       terminal
 [1, 4, 7, 8],  # 2:    1  =>  0   1 1   2   3   non-terminal
 [1, 4, 7, 8],  # 3:  0 1  =>  0   1 1   2   3       terminal
 [1, 4, 7, 8],  # 4:  1 1  =>  0   1 1   2   3       terminal
 [1, 4, 7, 8],  # 5:  2 1  =>  0   1 1   2   3       terminal
 [1, 4, 7, 8],  # 6:  3 1  =>  0   1 1   2   3       terminal
 [1, 5, 7, 8],  # 7:    2  =>  0   2 1   2   3       terminal
 [1, 6, 7, 8]]  # 8:    3  =>  0   3 1   2   3       terminal

# recurrent class: states 0 1 2 3 4

# memory tree

# |___0
# |___1___0 1
# |   |___1 1
# |   |___2 1
# |   |___3 1
# |___2
# |___3
