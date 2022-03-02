# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ExtractHistogram
	Extraction of a frequency distribution from an object of type 'data'.
  Usage
	ExtractHistogram(mixt_histo, mixt_type)
	ExtractHistogram(mixt_histo, "Component", index)
	ExtractHistogram(convol_histo, "Elementary", index)
	ExtractHistogram(convol_histo, "Convolution")
	ExtractHistogram(compound_histo, compound_type)
	
	ExtractHistogram(vec1)
	ExtractHistogram(vecn, variable)
	
	ExtractHistogram(timev, timev_type)
	ExtractHistogram(timev, "NbEvent", time)
	ExtractHistogram(renewal_data, renew_type)
	
	ExtractHistogram(seq, "Length")
	ExtractHistogram(seq1, "Value")
	ExtractHistogram(seqn, "Value", variable)
	ExtractHistogram(discrete_seq1, seq_type, value)
	ExtractHistogram(discrete_seqn, seq_type, variable, value)
	ExtractHistogram(simul_seq1, "Observation", value)
	ExtractHistogram(simul_seqn, "Observation", variable, value)
	
	ExtractHistogram(top, "Main")
	ExtractHistogram(top, "NbAxillary", position)	
  Arguments
	mixt_histo (mixture_data),
	mixt_type (string): type of frequency distribution: "Weight" or "Mixture",
	index (int): index of the elementary frequency distribution,
	convol_histo (convolution_data),
	compound_histo (compound_data),
	compound_type (string): type of frequency distribution: "Sum", "Elementary" or "Compound",
	
	vec1 (vectors): values,
	vecn (vectors): vectors,
	variable (int): variable index,
	
	timev (time_events, renewal_data),
	timev_type (string): type of frequency distribution: "ObservationTime" or "Mixture",
	time (int): observation period,
	renewal_data (renewal_data),
	renew_type (string): type of frequency distribution: "InterEvent", "Backward", "Forward", "LengthBias" or "Inside",
	
	seq (sequences, discrete_sequences, markov_data, semi-markov_data),
	seq1 (sequences, discrete_sequences, markov_data, semi-markov_data): univariate sequences,
	seqn (sequences, discrete_sequences, markov_data, semi-markov_data): multivariate sequences,
	discrete_seq1 (discrete_sequences, markov_data, semi-markov_data): discrete univariate sequences,
	discrete_seqn (discrete_sequences, markov_data, semi-markov_data): discrete multivariate sequences,
	simul_seq1 (markov_data, semi-markov_data): discrete simulated univariate sequences,
	simul_seqn (markov_data, semi-markov_data): discrete simulated multivariate sequences,
	seq_type (string): type of frequency distribution: "FirstOccurrence", "Recurrence", "Sojourn", "FinalRun", "NbRun" or "NbOccurrence",
	value (int): value,
	
	top (tops),
	position (int): position.
	
  Returned Object
	If the arguments (mixt_type, index, compound_type, timev_type, time, renew_type, seq_type, variable, value, position) defined an existing frequency distribution, an object of type HISTOGRAM is returned, otherwise no object is returned.
	
  See Also
	
	ExtractVectors, 
	Plot, 
	Compare (distributions), 
	ComparisonTest, 
	Estimate (distributions),
	Estimate (renewal process),
	Estimate (Markovian models),
	Estimate ('top' parameters),
	Fit.
"""
