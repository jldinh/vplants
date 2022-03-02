# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Switch
	Multi-conditional expression.
Usage
	Switch v Case v1 : e1 Case v2 : e2 Case ... Default ek
Arguments
	v (T). is any expression
	v1 (Ti). Ti can be any type.
	e1 (). can be any type.
Returned Object
	The object returned can have the same type as either e1, e2,...or ek.
Description
	This expression returns e1 if v = v1, e2 if v = v2, etc. It returns ek if none of the Case expressions matches v.
Side Effect
	Important: in the first version of AMAPmod, the evaluation procedure of expressions evaluates all subexpressions before evaluating a given expression. Thus, in every cases, both e1 and e2 are evaluated first. Then depending on the value of v the evaluation of the Switch expression leads to select either e1 or e2 or any other ei expression. This means that some time may be lost in computing useless expressions. This behavior will be corrected in version 2.
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Append.

Examples
	AML>Switch 1 + 3 Case 1 :"A" Case 2 : "B" Case 3 : "C" \
	AML> Case 4 : "D" Default : "Z"
	<STRING>D
	AML> # A function for coloring a PlantFrame (the argument
	enotes a plant entity)
	AML> color _order(_x) = Switch Order(_x) Case 1 : Black \
	AML> Case 2: Blue Case 3 : Green Case 4 : Red Default : Yellow
	<FUNC>Func.
	AML> f = PlantFrame(1,Scale -> 3)
	<PlantFrame> Standard.
	AML> Plot(f,Color -> color_order)
"""
