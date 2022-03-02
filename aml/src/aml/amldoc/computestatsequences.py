# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ComputeStateSequences
	Computation of the optimal state sequences corresponding to the observed sequences using a hidden Markov chain or a hidden semi-Markov chain.
  Usage
	ComputeStateSequences(seq, hmc, Algorithm->"ForwardBackward",
	Characteristics->True)
	ComputeStateSequences(seq, hsmc, Algorithm->"ForwardBackward",
	Characteristics->True)
	
  Arguments
	hmc (hidden_markov),
	hsmc (hidden_semi-markov),
	seq (discrete_sequences, markov_data, semi-markov_data).
	
  Optional Arguments 
	Algorithm (string): type of algorithm: "Viterbi" (the default) or "ForwardBackward".
	Characteristics (bool): computation of the characteristic distributions of the model taking into account the lengths of the segmented sequences (default value: False).
	
  Returned Object
	If the second mandatory argument is of type hidden_markov, an object of type markov_data is returned. If the second mandatory argument is of type hidden_semi-markov, an object of type semi-markov_data is returned. The returned object contains both the sequences (including the optimal state sequences as a supplementary variable) and the model.	
  Background
	This restoration of the state sequence is either performed by a dynamic programming algorithm referred to as Viterbi algorithm which maximizes the joint probability of the state and output sequence  (global criterion) or by a ‘forward-backward’ algorithm which chooses state j at time t to maximize  (local criterion).
	
  See Also
	ExtractHistogram.
"""
