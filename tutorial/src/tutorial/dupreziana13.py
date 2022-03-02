# MARKOV_CHAIN

# 3 STATES

# TRANSITION_PROBABILITIES      memory

transition_probability = \
[[0.99, 0.01, 0],     #  0:              initial
 [0.35, 0.56, 0.09],  #  1:      0   non-terminal
 [0.4,  0.41, 0.19],  #  2:    0 0   non-terminal
 [0.53, 0.43, 0.04],  #  3:  0 0 0       terminal
 [0.37, 0.4,  0.23],  #  4:  1 0 0       terminal
 [0.08, 0.47, 0.45],  #  5:  2 0 0       terminal
 [0.28, 0.7,  0.02],  #  6:    1 0       terminal
 [0.73, 0.23, 0.04],  #  7:    2 0       terminal
 [0.85, 0.14, 0.01],  #  8:      1   non-terminal
 [0.87, 0.12, 0.01],  #  9:    0 1       terminal
 [0.69, 0.31, 0],     # 10:    1 1       terminal
 [0.8,  0.2,  0],     # 11:    2 1       terminal
 [0.97, 0.03, 0]]     # 12:      2       terminal

# memory transition matrix

memory_transition = \
[[1 ,  8, 12],  #  0:   init  =>      0     1    2        initial
 [2 ,  9, 12],  #  1:      0  =>    0 0   0 1    2    non-terminal
 [3 ,  9, 12],  #  2:    0 0  =>  0 0 0   0 1    2    non-terminal
 [3 ,  9, 12],  #  3:  0 0 0  =>  0 0 0   0 1    2        terminal
 [3 ,  9, 12],  #  4:  1 0 0  =>  0 0 0   0 1    2        terminal
 [3 ,  9, 12],  #  5:  2 0 0  =>  0 0 0   0 1    2        terminal
 [4 ,  9, 12],  #  6:    1 0  =>  1 0 0   0 1    2        terminal
 [5 ,  9, 12],  #  7:    2 0  =>  2 0 0   0 1    2        terminal
 [6 , 10, 12],  #  8:      1  =>    1 0   1 1    2    non-terminal
 [6 , 10, 12],  #  9:    0 1  =>    1 0   1 1    2        terminal
 [6 , 10, 12],  # 10:    1 1  =>    1 0   1 1    2        terminal
 [6 , 10, 12],  # 11:    2 1  =>    1 0   1 1    2        terminal
 [7 , 11, 12]]  # 12:      2  =>    2 0   2 1    2        terminal

# recurrent class: states 0 1 2

# memory tree                        
                                     
# |___0___0 0___0 0 0                
# |   |     |___1 0 0                
# |   |     |___2 0 0                
# |   |___1 0                        
# |   |___2 0                        
# |___1___0 1                        
# |   |___1 1                        
# |   |___2 1                        
# |___2
