# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Compare
	Comparison of Markovian models.
  Usage
	
	Compare(mc1, length_histo1, mc2, length_histo2,…,
	FileName->"result")
	Compare(mc1, mc2,…, nb_seq, length, FileName->"result")
	Compare(mc1, seqm1, mc2, seqm2,…, nb_seq, FileName->"result")
	Compare(smc1, length_histo1, smc2, length_histo2,…,
	FileName->"result")
	Compare(smc1, smc2,…, nb_seq, length, FileName->"result")
	Compare(smc1, seqm1, smc2, seqm2,…, nb_seq, FileName->"result")
	Compare(hmc1, length_histo1, hmc2, length_histo2,…,
	FileName->"result")
	Compare(hmc1, hmc2,…, nb_seq, length, FileName->"result")
	Compare(hmc1, seqm1, hmc2, seqm2,…, nb_seq, FileName->"result")
	Compare(hsmc1, length_histo1, hsmc2, length_histo2,…,
	FileName->"result")
	Compare(hsmc1, hsmc2,…, nb_seq, length, FileName->"result")
	Compare(hsmc1, seqm1, hsmc2, seqm2,…, nb_seq,
	FileName->"result")
	
  Arguments
	mc1, mc2, … (markov),
	smc1, smc2, … (semi-markov),
	hmc1, hmc2, … (hidden_markov),
	hsmc1, hsmc2, … (hidden_semi-markov),
	length_histo1, length_histo2, … (histogram, mixture_data, convolution_data, compound_data): frequency distribution of lengths of generated sequences,
	nb_seq (int): number of generated sequences,
	length (int): length of generated sequences,
	seqm1, seqm2, … (discrete_sequences, markov_data, semi-markov_data).
	
  Optional Arguments 
	FileName (string): name of result file. If this optional argument is used, some complementary results, with respect to the returned object of type distance_matrix, are saved on a file.
	
  Returned Object
	An object of type distance_matrix is returned.	
  Background
	The comparison of Markovian models relies on the Kullback-Leibler directed divergence (or cross-entropy or discriminant information). For each model being compared, a sample of sequences is generated and the log-likelihoods of these sequences for the different models are computed (including the reference model used for simulation). The dissimilarity measure is the ‘divergence’ from the reference model to the target model on the basis of log-likelihoods of the sequences normalized by their cumulative length. This procedure is repeated for each model.
	
  See Also
	Estimate (Markovian models).
"""
