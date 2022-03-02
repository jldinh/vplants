# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
VarianceAnalysis
	One-way variance analysis.
  Usage
	VarianceAnalysis(vec, class_variable, response_variable, type,
	FileName->"result", Format->"SpreadSheet")
	
  Arguments
	vec (vectors), 
	class_variable (int): index of the class or group variable,
	response_variable (int): index of the response variable,
	type (string): type of the response variable ("NUMERIC" ("N") or "ORDINAL" ("O")).
	
  Optional Arguments 
	FileName (string): name of the result file,
	Format (string): format of the result file: "ASCII" (default format) or "SpreadSheet". This optional argument can only be used in conjunction with the optional argument FileName.
	
  Returned Object
	No object returned.
  Description
	The result of the variance analysis is displayed in the shell window.
"""
