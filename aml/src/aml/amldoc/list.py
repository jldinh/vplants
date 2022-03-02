# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
List
	List constructor
Usage
	List(x1,x2,...,xn)
Arguments
	x1,x2,...,xn (T1,T2,...,TN) : Type TK, , can be any type. Any xk can be Undef.
Returned Object
	If the type of the arguments xk is TK, the value returned by a set constructor is an LIST(T1,T2,...,TN).
Description
	A List is a set-type, i.e. the type of a collection of objects. Contrary to ARRAYs and SETs, LIST collections are heterogenous collection of objects. Elements of a LIST can have the different types. The order of the elements of a LIST is relevant.
Details
	 In version 1.x of AMAPmod there is no way of saving or loading binary or ASCII representations of lists.
	 There is no possibility to Plot LISTs.
	 Two LISTs are equal if they have the same elements, in the same order.
	
See Also
	
	Size, 
	Sum, 
	Array, 
	Set, 
	ToArray, 
	ToSet, 
	ToList, 
	At, 
	Pos, 
	AllPos, 
	Head, 
	Tail, 
	InsertAt, 
	RemoveAt, 
	Invert.
	

Examples
	AML>l = List("A",7)
	<LIST(STRING,INT)> [A,7]
	AML> l = List("A",Undef,7)
	<LIST(STRING,UNDEF,int)> [A,Undef,7]
	AML> l@3
	<INT> 7
	AML> l = List(Undef,Undef,Undef)
	<LIST(UNDEF,UNDEF,UNDEF,UNDEF)> [Undef,Undef,Undef]
	AML> l = List("A",7,List([1,2],True))
	<LIST(STRING,INT,LIST(ARRAY(INT),BOOL))> 
	[A,7,[[1,2],TRUE]]
"""
