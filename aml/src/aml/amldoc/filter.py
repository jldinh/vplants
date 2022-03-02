# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Filter
	Applies a linear filter to an array, which outputs an array made of locally weighted mean values of the initial array. 

Usage
	Filter(array, filt)
Arguments
	array (ARRAY(T)). T is either INT or REAL. array is the array to be filtered. 
      filt (ARRAY(T')). T' is either INT or REAL. filt is the array used to filter array. filt must have an odd number of elements. 
	
Returned Object
	The function returns an element of type ARRAY(REAL). If the argument is Undef, returns Undef.
Description
	This function is used to apply a linear filter to an array of numeric values. This can be used for instance to smooth a series of values by replacing each value of the initial array array by a mean of its neibourgh values. Let us denote 
	array=
	and filt=
	Since k is an odd number, let us denote . Then the function Filter returns an array whose ith element is given by:
 	
	with the convention that  if  and 1 otherwise. In this case the sum at the denominator is limited to j such that . If for some i, the value of this sum happens to be null, the division is not made and the result is simply
	.
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Head,
	MovingAverage.
 	

Examples
	  AML> Filter([1,5,2,1,-7,1,1,1,1,9,1,1,1,1],[1,1,1,1,1]) \
      AML> # smoothes a series of values
      <ARRAY(INT)> [2.67,2.25,0.4,0.4,-0.4,-0.6,
      -.6,2.6,2.6,2.6,2.6,2.6,1,1]
      AML> Filter([1,5,2,1,-7,1,1,1,1,9,1,1,1,1],[1,-2,1]) \
      AML> # emphasizes the deviations
      <SET(INT)> [-3,-7,2,-7,16,-8,0,0,8,-16,8,0,0,1]
"""
