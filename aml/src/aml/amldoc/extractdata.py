# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ExtractData
	Extraction of the 'data' part of an object of type 'model'.
  Usage
	ExtractData(mixt)
	ExtractData(convol)
	ExtractData(compound)
	
	ExtractData(hmc)
	ExtractData(hsmc)	
  Arguments
	mixt (mixture),
	convol (convolution),
	compound (compound),
	
	hmc (hidden_markov),
	hsmc (hidden_semi-markov).
	
  Returned Object
	
	 If mixt contains a 'data' part, an object of type mixture_data is returned, otherwise no object is returned.
	 If convol contains a 'data' part, an object of type convolution_data is returned, otherwise no object is returned.
	 If compound contains a 'data' part, an object of type compound_data is returned, otherwise no object is returned.
	 If hmc contains a 'data' part, an object of type markov_data is returned, otherwise no object is returned.
	 If hsmc contains a 'data' part, an object of type semi-markov_data is returned, otherwise no object is returned.
	
  Description
	This function enables to extract the 'data' part of an object of type 'model' when the estimation of model parameters from data gives rise to the construction of pseudo-data. This situation is notably exemplified by the computation of optimal state sequences from estimated hidden Markovian processes (optional argument StateSequences of the function Estimate set at "ForwardBackward" or "Viterbi").
	
  See Also
	
	Estimate (distributions),
	Estimate (Markovian models).
"""
