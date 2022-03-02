# -*- python -*-
#
#       physics: physics algorithms
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
"""
node definition for chemistry package
"""

__license__= "Cecill-C"
__revision__=" $Id: chemistry.py 7882 2010-02-08 18:36:38Z cokelaer $ "

from openalea.core import ScriptLibrary
from openalea.physics.chemistry import FixedConcentration,FixedFlux,\
                             Reaction,\
                             GraphDiffusion

def diffusion (graph, D, V, subst, dt) :
	"""Diffuse a substance.
	"""
	def func () :
		algo = GraphDiffusion(graph,V,D)
		algo.react(subst,dt)
	
	return func,

def diffusion_script (inputs, outputs) :
	lib = ScriptLibrary()
	graph,D,V,subst,dt = inputs
	graph,script = lib.name(graph,"")
	D,script = lib.name(D,script)
	V,script = lib.name(V,script)
	subst,script = lib.name(subst,script)
	func, = outputs
	func = lib.register(func,"func")
	
	script += "def %s () :\n" % func
	script += "\tfrom openalea.physics.chemistry import GraphDiffusion\n"
	script += "\t\n"
	script += "\talgo = GraphDiffusion(%s,%s,%s)\n" % (graph,V,D)
	script += "\talgo.react(%s,%f)\n\n" % (subst,dt)
	
	return script

def reaction (alpha, beta, subst, dt) :
	"""Creation decay reactions.
	"""
	def func () :
		algo = Reaction(alpha,beta)
		algo.react(subst,dt)
	
	return func,

def reaction_script (inputs, outputs) :
	lib = ScriptLibrary()
	alpha,beta,subst,dt = inputs
	alpha,script = lib.name(alpha,"")
	beta,script = lib.name(beta,script)
	subst,script = lib.name(subst,script)
	func, = outputs
	func = lib.register(func,"func")
	
	script += "def %s () :\n" % func
	script += "\tfrom openalea.physics.chemistry import Reaction\n"
	script += "\t\n"
	script += "\talgo = Reaction(%s,%s)\n" % (alpha,beta)
	script += "\talgo.react(%s,%f)\n\n" % (subst,dt)
	
	return script


