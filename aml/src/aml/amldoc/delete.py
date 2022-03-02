# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Delete
	Delete an object from the current set of AML objects.
Usage
	Delete(name1, name2, ...)
Arguments
	name1, name2,... (STRING) : names of the object to be deleted.
Returned Object
	No value is returned.
Description
	The objects passed as arguments are deleted from the set of AML objects. This means that the name of the corresponding variables is no longer used and that the corresponding memory zone is freed.
Note
	Since the a AML variable is designated by its name, this name is always evaluated to the corresponding AML object and not to a STRING. Therefore, to apply Delete correctly to a variable whose name is var1 for instance, one has to explicitly write Delete("var1") or more simply Delete("var1") (the quote character before a STRING name suppress the evaluation of the STRING).
See Also


Examples
	AML>I = 9; j="Hello"; var1=[1,2,3]
	<ARRAY(INT)> [1,2,3]
	AML> ?
	I INT :9
	J STRING :Hello
	var1 ARRAY(INT) [1,2,3]
	AML> Delete('i,'var1)
	AML> ?
	j STRING Hello
"""
