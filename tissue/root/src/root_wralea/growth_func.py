from math import exp

def growth_func():
    '''    
    '''
    def func (x) :
        if x < 100 :
            return 0.
        elif x > 3000. :
            return 10.
        else :
            return (x - 100.) / 2900.*10.
    return func,

def growth_func2():
    '''    
    '''
    def func (x) :
        if x < 100 :
            return 0.
        elif x > 3300. :
            return 10.
        else :
            return (x - 100.) / 3200.*10.
    return func,

def sigmoid_func (K, xmax) :
	"""Return a growth accelerating from 0
	for x = 0 up to a given threshold 
	reached for x = xmax
	"""
	def func (x) :
		if x < 0. :
			return 0.
		elif x > xmax :
			return K
		else :
			return K / (1 + exp(-(x / xmax - 0.5) * 10.) )
	
	return func,

def linear_func (K, xmax) :
	"""Return a growth accelerating from 0
	for x = 0 up to a given threshold 
	reached for x = xmax
	"""
	def func (x) :
		if x < 0. :
			return 0.
		elif x > xmax :
			return K
		else :
			return K * x / xmax
	
	return func,

