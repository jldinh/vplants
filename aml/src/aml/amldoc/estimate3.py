# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Estimate
	Estimation of (hidden) Markovian models.
  Usage
	Estimate(seq, "MARKOV", Order->2, Counting->False)
	Estimate(seq, "MARKOV", MaxOrder->3, Penalty->"AIC",
	Counting->False) 
	Estimate(seq, "MARKOV", states, Penalty->"AIC", Order->2,
	Counting->False) 
	
	Estimate(seq, "NON-HOMOGENEOUS_MARKOV", MONOMOLECULAR, VOID, 
	Counting->False) 
	
	Estimate(seq, "SEMI-MARKOV", Counting->False)
	
	Estimate(seq, "HIDDEN_MARKOV", nb_state, structure,
	SelfTransition->0.9, NbIteration->10, 
	StateSequences->"Viterbi", Counting->False) 
	Estimate(seq, "HIDDEN_MARKOV", hmc, Algorithm->"Viterbi",
	NbIteration->10, Order->2, Counting->False) 
	Estimate(seq, "HIDDEN_MARKOV", "NbState", min_nb_state,
	max_nb_state, Penalty->"AIC", Order->2, 
	Counting->False) 
	Estimate(seq, "HIDDEN_MARKOV", "NbState", hmc, state,
	max_nb_state, Penalty->"AIC", SelfTransition->0.9, 
	Counting->False) 
	
	Estimate(seq, "HIDDEN_SEMI-MARKOV", nb_state, structure,
	OccupancyMean->20, NbIteration->10, 
	Estimator->"PartialLikelihood",
	StateSequences->"Viterbi", Counting->False) 
	Estimate(seq, "HIDDEN_SEMI-MARKOV", hsmc, Algorithm->"Viterbi",
	NbIteration->10, Counting->False) 
	
  Arguments
	seq (discrete_sequences, markov_data, semi-markov_data),
	states, ... (array(int)): new states corresponding to a partition of the original state space,
	hmc (hidden_markov),
	structure (string): structural properties of  the underlying Markov chain: "Irreductible" or "LeftRight" (i.e. a succession of transient states and a final absorbing state),
	nb_state (int): number of states with 2 £ nb_state £  15,
	min_nb_state (int): minimum number of states,
	max_nb_state (int): maximum number of states with 2 £ min_nb_state < max_nb_state £ 15 or (number of states of the initial hidden Markov chain hmc) < max_nb_state £ 15.
	state (int): state to be duplicated,
	hsmc (hidden_semi-markov).
	
  Optional Arguments 
	Counting (bool): computation of counting distributions (default value: True).
	
	Order (int): Markov chain order (default value: 1). This optional argument can only be used if the second mandatory argument giving the model type is "MARKOV", "NON-HOMOGENEOUS_MARKOV" or "HIDDEN_MARKOV".
	MaxOrder (int): maximum order of the Markov chain (default value: 4). This optional argument can only be used if the second mandatory argument giving the model type is "MARKOV".
	
	Penalty (string): type of penalty function for model selection: "AIC" (Akaike Information Criterion), "AICc" (corrected Akaike Information Criterion) or "BIC" (Bayesian Information Criterion). This optional argument can only be used if the second mandatory argument giving the model type is "MARKOV" (default value: "BIC") and if the optional argument MaxOrder is set or else, if a new set of states is given (defining a partition of the original state space) or else, if the second mandatory argument giving the model type is "HIDDEN_MARKOV" and the third "NbState" (default value: "AICc").
	
	Algorithm (string): type of algorithm: "ForwardBackward" (the default) or "Viterbi". This optional argument can only be used if the second mandatory argument giving the model type is "HIDDEN_MARKOV" or "HIDDEN_SEMI-MARKOV".
	NbIteration (int): number of iterations of the estimation algorithm.
	SelfTransition (real): self-transition probability. This optional argument can only be used if the second mandatory argument giving the model type is "HIDDEN_MARKOV" and if the initial model used in the iterative estimation procedure (EM algorithm) is only specified by its number of states, its structural properties and eventually its order.
	OccupancyMean (int/real): average state occupancy. This optional argument can only be used if the second mandatory argument giving the model type is "HIDDEN_SEMI-MARKOV" and if the initial model used in the iterative estimation procedure (EM algorithm) is only specified by its number of states and its structural properties.
	Estimator (string): type of estimator: "CompleteLikelihood" (the default) or "PartialLikelihood". In this latter case, the contribution of the time spent in the last visited state is not taken into account inthe estimation of the state occupancy distributions. This optional argument can only be used if the second mandatory argument giving the model type is "HIDDEN_SEMI-MARKOV" and the optional argument Algorithm is set at "ForwardBackward". 
	StateSequences (string): Computation of the optimal state sequences: no computation (the default), "ForwardBackward" or "Viterbi". This optional argument can only be used if the second mandatory argument giving the model type is "HIDDEN_MARKOV" or "HIDDEN_SEMI-MARKOV" and if the optional argument Algorithm is not set at "Viterbi".
	
  Returned Object
	In case of success of the estimation procedure, the type of the returned object (chosen among markov, semi-markov, hidden_markov, hidden_semi-markov) is given by the second mandatory argument. Otherwise no object is returned. If the second mandatory argument is "NON-HOMOGENEOUS_MARKOV", in case of success of the estimation procedure, the returned object is of type markov. If the second mandatory argument is "NON-HOMOGENEOUS_MARKOV", the subsequent arguments chosen among "VOID" (homogeneous state), "MONOMOLECULAR" or "LOGISTIC", specify the evolution of the self-transition probabilities as a function of the index parameter. The returned object of type markov, semi-markov, hidden_markov or hidden_semi-markov contains both the estimated distribution and the data used in the estimation procedure. In the case of the estimation of a hidden Markov chain or a hidden semi-Markov chain, the returned object contains pseudo-data (optimal state sequences corresponding to the observed sequences used in the estimation procedure) computed as a byproduct of the EM algorithm which can be extracted by the function ExtractData.
  Description
	In the case of hidden Markovian models (second mandatory argument "HIDDEN_MARKOV" or "HIDDEN_SEMI-MARKOV"), either the forward-backward algorithm or the Viterbi algorithm can be used for estimation. The Viterbi algorithm should only be used for the estimation of hidden Markovian models based on an underlying "left-right" Markov chain (i.e. constituted of a succession of transient states and a final absorbing state). Hence, in this case, the model structure is implicitly "LeftRight" and should not be given as argument (only the number of states should be given as argument). Since the optimal state sequences are computed by the Viterbi algorithm, the optional argument StateSequences cannot be used if the optional argument Algorithm is set at "Viterbi".
	
  See Also
	
	AddAbsorbingRun,
	ExtractData,
	ExtractDistribution,
	ModelSelectionTest.
"""
