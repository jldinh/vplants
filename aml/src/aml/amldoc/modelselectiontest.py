# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ModelSelectionTest
	Test of the order of a Markov chain or of a possible partition of the original state space (lumpability hypothesis).
  Usage
	ModelSelectionTest(seq, order0, order1)
	
	ModelSelectionTest(seq, states, Order->2)	
  Arguments
	seq (discrete_sequences, markov_data, semi-markov_data),
	
	order0 (int): order corresponding to the null hypothesis,
	order1 (int): order corresponding to the alternative hypothesis,
	
	states, ... (array(int)): new states corresponding to a partition of the original state space,
	
  Optional Arguments 
	Order (int): order of the Markov chain (default value: 1). This optional argument can only be used when testing a lumpability hypothesis.
	
  Returned Object
	No object returned.
  Description
	The result of the test is displayed in the shell window.	
  Background
	If 0 <= order0 < order1, a likelihood ratio statistic is constructed from the observed frequencies of transitions according to the two hypotheses of order of the Markov chain. This statistic has a c2 distribution with k degrees of freedom (k = (number of free parameters of the order1 Markov chain) - (number of free parameters of the order0 Markov chain)).
	
	When testing a lumpability hypothesis, a likelihood ratio statistic is constructed from the observed frequencies of transitions (and observations in the case of the lumped process) according to the two hypotheses. This statistic has a c2 distributions with k degrees of freedom (k = (number of free parameters of the original Markov chain) - (number of free parameters of the lumped process)).
	
  See Also
	Estimate (Markovian models).
"""
