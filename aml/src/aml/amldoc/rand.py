# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Rand
	Computes a random value.
Usage
	
	Rand()
	Rand(i,j)
	
Arguments
	i, j (INT). j must be greater i.
Returned Object
	If no argument is given, Rand returns a REAL between 0 and 1 (following a uniform distribution). If two arguments are given, Rand returns and INT at random between i and j.
Description
	Based on Linux function Random().
See Also
	STAT module

Examples
  AML>Rand()
	<REAL> 0.45675
  AML>Rand(22,35)
	<REAL> 28
	# Rand is evaluated only once in the following iteration:
  AML>Foreach _i In [1,5] : Rand(22,35)
	<REAL> [34,34,34,34,34]
	# The following trick is used to have Rand evaluated for
	# each _i :
  AML>Foreach _i In [1,5] : Rand(22,35+_i-_i)
	<REAL> [29,29,31,22,25]
"""
