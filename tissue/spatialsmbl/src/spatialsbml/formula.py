# -*- python -*-
#
#       spatialsbml: Spatial templating of SBML
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
This module define functions to modify AST formulas
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

def variables (formula) :
	"""Iterate on all variable names in this formula
	
	:Parameters:
	 - `formula` (ASTNode) - a mathml description
	
	:Returns Type: iter of str
	"""
	#warning this function is recursive
	if formula.isName() :
		yield formula.getName()
	
	for i in xrange(formula.getNumChildren() ) :
		for var in variables(formula.getChild(i) ) :
			yield var

def _replace (node, old_txt, new_txt) :
	"""Internal function
	
	Perform `replace` recursively on the given node
	"""
	if node.isName() :
		name = node.getName()
		if name == old_txt :
			node.setName(new_txt)
	
	for i in xrange(node.getNumChildren() ) :
		_replace(node.getChild(i),old_txt,new_txt)

def replace (formula, old_txt, new_txt) :
	"""Replace all occurence of old_txt by new_txt
	
	Create a new formula, copy of the given one where
	all occurences of old_txt have been replaced by new_txt
	
	:Parameters:
	 - `formula` (ASTNode) - a mathml description
	 - `old_txt` (str) - the txt to find
	 - `new_txt` (str) - old txt will be replaced by this one
	
	:Returns type: ASTNode
	"""
	#create a copy
	formula = formula.deepCopy()
	#replace txt
	_replace(formula,old_txt,new_txt)
	#return
	return formula
