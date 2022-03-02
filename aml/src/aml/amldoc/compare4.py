# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Compare
	Comparison of Markovian models for sequences.
  Usage
	Compare(discrete_seq, mc1, mc2,…, FileName->"result")
	Compare(discrete_seq, smc1, smc2,…, FileName->"result")
	Compare(discrete_seq, hmc1, hmc2,…, Algorithm->"Viterbi",
	FileName->"result")
	Compare(discrete_seq, hsmc1, hsmc2,…, Algorithm->"Viterbi",
	FileName->"result")
	
  Arguments
	discrete_seq (discrete_sequences, markov_data, semi-markov_data),
	mc1, mc2, … (markov),
	smc1, smc2, … (semi-markov),
	hmc1, hmc2, … (hidden_markov),
	hsmc1, hsmc2, … (hidden_semi-markov).
	
  Optional Arguments 
	Algorithm (string): type of algorithm: "Forward" (the default) or "Viterbi". This optional argument applies only with models of type hidden_markov or hidden_semi-markov,
	FileName (string): name of result file.
	
  Returned Object
	No object returned.
  Description
	The result of comparisons is displayed in the shell window.	
  Background
	In the case of Markov chains (type markov) or semi-Markov chains (type semi-markov), the comparison relies on the likelihood of a sequence for the different models being compared. In the case of hidden Markov chains (type hidden_markov) or hidden semi-Markov chains (hidden_semi-markov), the comparison relies either on the likelihood of a sequence (of every possible state sequences that can generate the observed sequence: Algorithm->"Forward"), or on the likelihood of the state sequence that best explains the observed sequence (Algorithm->"Viterbi").
	
  See Also
	ComputeStateSequences.
"""
