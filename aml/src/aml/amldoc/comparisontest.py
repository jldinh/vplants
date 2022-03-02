# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ComparisonTest
	Test of comparaison of frequency distributions.
  Usage
	ComparisonTest(type, histo1, histo2)	
  Arguments
	type (string): type of test: "F", "T" or "W" (Wilcoxon-Mann-Whitney),
	histo1, histo2 (histogram, mixture_data, convolution_data, compound_data).
	
  Returned Object
	No object returned.
  Description
	The result of the test is displayed in the shell window.	
  Background
	The objective is to compare two independent random samples in order to decide if they have been drawn from the same population or not.
	In the case of samples from normal populations, the Fisher-Snedecor ("F") test enables to test is the two variances are not significantly different. The normal distribution assumption should be checked for instance by the exam of the shape coefficients (skewness and kurtosis coefficients). The test statistic is:
	
	where  and  are the means of the samples.
	The Fisher-Snedecor variable  with  degrees of freedom and  degrees of freedom can be interpreted as the ratio of the variance estimators of the two samples. In practice, the larger estimated variance is put at the denominator. Hence . The critical region is of the form  (one-sided test).
	In the case of samples from normal populations with equal variances, the Student ("T") test enables to test if the two means are not significantly different. The test statistic is:
	
	The critical region is of the form  (two-sided test). For sufficiently large sample sizes, this test of sample mean comparison can be used for samples from non-normal populations with unequal variances. This test is said to be robust.
"""
