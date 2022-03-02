# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Set
    Set constructor
Usage
	Set(x1,x2,...,xn)
Arguments
	x1,x2,...,xn (T) : values of identical type. Type T can be any type. Any xk can be Undef.
Returned Object
	If the type of the arguments xk is T, the value returned by a set constructor is an SET(T) if at least one xk is not Undef. If all xk are Undef the constructor returns Undef.
Description
	A SET is a set-type, i.e. the type of a collection of objects. Like for ARRAYs, all the elements of a SET must have the same type. However, a SET can contain Undef elements. Contrary to ARRAYs, elements of a SET are not ordered. It is thus meaningless to speak of the ith element of a SET. Consequently, each element of a set appears only once in the SET. There are no duplicates of elements.
Details
	 In version 1.x of AMAPmod there is no way of saving or loading binary or ASCII representations of sets. For ASCII representations, one may want to save a SET as an ARRAY:
	AML> Save(ToArray(set1),"filename")
	Then, it is possible to load an ASCII ARRAY and to cast it to a Set:
	AML> ToSet(Array("filename"))
	 There is no possibility to Plot Sets.
	 Two sets are equal if they contain the same elements (no matter the order). The semantics of the equality between two elements is either straightforward (e.g. equality beween to integers or between an integer and a REAL, etc.) or defined in the constructor man page of the element.
See Also
	
	Size, 
	Sum, 
	Array, 
	List, 
	ToArray, 
	ToSet, 
	ToList.

Examples
	AML> s=Set(2,3,10,3,2,2,2,10,11,2)
	<ARRAY(INT)> [2,3,10,11]
	AML> s=Set(2,3,Undef,3,Undef)
	<ARRAY(INT)>[2,3,Undef]
	AML> s=Set([1,2,3],[9],[],[1,2,3],[9])
	<ARRAY(ARRAY((INT))>[[],[9],[1,2,3]]
"""
