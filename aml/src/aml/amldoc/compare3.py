# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Compare
	Comparison of sequences.
  Usage
	Compare(seq, vector_distance, RefSequence->3, TestSequence->8,
	Begin->"Free", End->"Free", Transposition->True,
	FileName->"result", Format->"SpreadSheet",
	AlignmentFileName->"alignment",
	AlignmentFormat->"ASCII")
	Compare(seq, RefSequence->3, TestSequence->8,
	Begin->"Free", End->"Free", 
	FileName->"result", Format->"SpreadSheet",
	AlignmentFileName->"alignment",
	AlignmentFormat->"ASCII")
	
  Arguments
	
	seq (sequences, discrete_sequences, markov_data, semi-markov_data),
	vector_distance (vector_distance).
	
  Optional Arguments 
	
	RefSequence (int): identifier of the reference sequence,
	TestSequence (int): identifier of the test sequence,
	Begin(STRING: "Free" or "Fixed" (the default). If this optional argument is set at "Free", any space at the beginning of the alignment contrid=bute a weight of 0 (beginning-space free alignment). 
	End(STRING: "Free" or "Fixed" (the default). If this optional argument is set at "Free", any space at the beginning of the alignment contrid=bute a weight of 0 (end-space free alignment).
	Transposition (bool): use of the transposition operation (default value: False). This optional argument requires the second mandatory argument being of type vector_distance.
	FileName (string): name of result file,
	Format (string): format of result file: "ASCII" (default format) or "SpreadSheet". This optional argument can only be used in conjunction with the optional argument FileName.
	AlignmentFileName (string): file name of the sequences of edit operations (deletion/insertion/exact matching and eventually substitution and transposition) resulting from sequence alignments,
	AlignmentFormat (string): format of the file of sequences of edit operations: "ASCII" (default format) or "Binary". This optional argument can only be used in conjunction with the optional argument AlignmentFileName.
	
  Returned Object
	An object of type distance_matrix is returned.
  Description
	If number of alignments £ 30, the alignments are displayed in the shell window.	
  Background
	The result of the comparison of two sequences takes the form of the sequence of edit operations required for transforming the reference sequence into the test sequence with associated costs:
	 deletion (‘d’): deletion of an element of the reference sequence,
	 insertion (‘i’): insertion of an element of the test sequence,
	 exact matching (‘m’): matching of an element of the test sequence with the same element in the reference sequence: null cost,
	 substitution (‘s’) (mismatching): replacement of an element of the reference sequence by another element of the test sequence: The associated cost is the standardized distance between the two elements.
	 transposition (two successive ‘t’) or swap: interchange of adjacent elements in the sequence with the additional constraint that each element can participate in no more than one swap. This edit operation applies only in the case where two successive element in the reference sequence exactly match two successive elements in the test sequence taken in reverse order.
	A purely structural alignment consists in allowing only exact matching, insertion and deletion. In this case, the argument vector_distance specifying the local distance between elements is not required.
	
  See Also
	VectorDistance, 
	Clustering.
"""
