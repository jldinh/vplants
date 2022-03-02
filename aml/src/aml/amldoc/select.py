# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Select
	Conditional identity function
Usage
	Select(exp, pred)
Arguments
	exp (ANY): argument that can be selected. This argument can have thevalue Undef
	pred (BOOL): argument that enables/disable the selection of the value ofthe first argument
Returned Object
	Select returns exp if pred is True, VOID if pred is False. If exp is Undef, returns Undef if pred is True and returns no value otherwise. If pred is Undef, returns Undef.
Description
	Select is the identity function if its second argument is True, and returns no value (VOID) if False. If pred has value Undef, Select returns Undef whatever the value of exp.

Examples
	AML>Select(3,True)
	<INT>3
	AML> Select(3,False)
	<VOID>
	AML> Select(Undef,True)
	<UNDEF> Undef
	AML> Select(Undef,False)
	<VOID>
	AML> #Filtering an array of values
	AML> Foreach _i In [1,2,3,2,2,4,1,1] : Select(_i,_i!=2)
	<ARRAY(INT)>[1,3,4,1,1]
"""
