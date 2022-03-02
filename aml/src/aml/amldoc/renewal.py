# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Renewal
	Construction of a (either ordinary or equilibrium) renewal process from an inter-event distribution or from an ASCII file.
  Usage
	Renewal("BINOMIAL", inf_bound, sup_bound, proba,
	Type->"Equilibriun", ObservationTime->40)
	Renewal("POISSON", inf_bound, param, Type->"Equilibriun",
	ObservationTime->40)
	Renewal("NEGATIVE_BINOMIAL", inf_bound, param, proba,
	Type->"Equilibriun", ObservationTime->40)
	
	Renewal(inter_event, Type->"Equilibriun", ObservationTime->40)
	
	Renewal(file_name, Type->"Equilibriun", ObservationTime->40)	
  Arguments
	inf_bound (int): lower bound to the range of possible values (shift parameter),
	sup_bound (int): upper bound to the range of possible values (only relevant for binomial or uniform distributions),
	param (int, real): parameter of either the Poisson distribution or the negative binomial distribution.
	proba (int, real): probability of 'success' (only relevant for binomial or negative binomial distributions).
	Remark: the names of the parametric discrete distributions can be summarized by their first letters: "B" ("BINOMIAL"), "P" ("POISSON"), "NB" ("NEGATIVE_BINOMIAL").
	
	inter_event (distribution, mixture, convolution, compound): inter-event distribution,
	file_name (string).
	
  Optional Arguments 
	Type (string): type of renewal process: "Ordinary" or "Equilibriun" (the default).
	ObservationTime (int): length of the observation period for the computation of the intensity and counting distributions (default value: 20),
	
  Returned Object
	If the construction succeeds, an object of type renewal is returned, otherwise no object is returned.	
  Background
	A renewal process is built from a discrete distribution termed the inter-event distribution which represents the time interval between consecutive events. Two types of renewal processes are available:
	 ordinary renewal process where the start of the observation period coincides with the occurrence time of an event (synchronism assumption),
	 equilibrium or stationary renewal process where the start of the observation period is independent of the process which generates the data (asynchronism assumption).
	In the case where the arguments are the name and the parameters of the inter-event distribution, the constraints on parameters described in the definition of the syntactic form of the type distribution apply (cf. File Syntax).
	
  See Also
	Save, 
	Simulate (renewal process)
"""
