# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
If-Then-Else
	Conditional expression.
Usage
	If Then else 
Arguments
	pred (BOOL). Boolean expression which expresses the condition
	e1 (T1). T1can be any type.
      e2 (T2). T2can be any type.
      
Returned Object
	Depending on the pred value, the object returned has the same type as either e1 or e2.
Description
	This expression returns e1 if pred is True. It returns e2 otherwise.
Side Effect
	Important: in the first version of AMAPmod, the evaluation procedure of expressions evaluates all subexpressions before evaluating a given expression. Thus, in every cases, both e1 and e2 are evaluated first. Then depending on the value of pred the evaluation of the If Then Else expression leads to select either e1 or e2. This means that some time may be lost in computing useless expressions. This behavior will be corrected in version 2.
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Append.
	

Examples
	AML> A = 3
	<INT>
	AML> If a == 3 Then "Yes" Else "No"
	<STRING>Yes
	AML> f(_x) = If _x == 3 Then "Yes" Else _x-1
	<FUNC> Function
	AML> f(2)
	<INT> 1
	AML> f(3)
	<STRING> Yes
"""
