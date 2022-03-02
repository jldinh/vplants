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
This module define function to analyse SBML templates
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from formula import variables

def _param_cpt (param, cpts) :
	"""Try to find in which compartment this parameter is defined
	
	By convention, if a parameter A is defined in a compartment cpt, its
	name is 'A_cpt' or 'A_XX_cpt_YY' where XX and YY may be anything except
	another compartment name.
	
	:Parameters:
	 - `param` (str) - name of the parameter to analyse
	 - `cpts` (set of str) - set of compartments name used in the model
	
	:Returns: the name of the compartment or None if nothing found
	
	:Returns Type: str
	"""
	for name in param.split("_") :
		if name in cpts :
			return name
	
	return None

def summary (model) :
	"""Print a summary of the given model
	
	:Parameters:
	 - `sbmtpl` (SBMLmod) - a template of SBML as returned by lisbml
	"""
	print "compartment"
	for cpt in model.getListOfCompartments() :
		name = cpt.getId()
		if name != "neighbor" :
			print "    - %s (type '%s')" % (name,cpt.getCompartmentType() )
	
	print "species"
	for sp in model.getListOfSpecies() :
		cpt = sp.getCompartment()
		if cpt != "neighbor" :
			print "    - %s (type '%s', defined in %s)" % (sp.getId(),
			                                              sp.getSpeciesType(),
			                                              cpt)
	
	print "global parameters"
	for param in model.getListOfParameters() :
		print "    - %s" % param.getId()
	
	print "reactions"
	for reaction in model.getListOfReactions() :
		reactants = []
		for spr in reaction.getListOfReactants() :
			nb = int(spr.getStoichiometry() )
			if nb == 1 :
				reactants.append(spr.getSpecies() )
			else :
				reactants.append("%d.%s" % (nb,spr.getSpecies() ) )
		
		reactants_str = "+".join(reactants)
		
		products = []
		for spr in reaction.getListOfProducts() :
			nb = int(spr.getStoichiometry() )
			if nb == 1 :
				products.append(spr.getSpecies() )
			else :
				products.append("%d.%s" % (nb,spr.getSpecies() ) )
		
		products_str = "+".join(products)
		
		modifiers = reaction.getListOfModifiers()
		
		print "    %s :" % reaction.getId()
		if len(modifiers) > 0 :
			modifiers_str = "(%s)" % (",".join(sp.getSpecies() \
			                            for sp in modifiers) )
			print "      %s -%s> %s" % (reactants_str,
			                            modifiers_str,
			                            products_str)
		else :
			print "      %s -> %s" % (reactants_str,products_str)
		
		print "      K = %s\n" % reaction.getKineticLaw().getFormula()

def analyse (sbmtpl) :
	"""Analyse a SMBL template
	
	This function takes an SBML template and analyse it to list:
	 - compartments types
	 - species types
	 - wether or not this template requiers neighborhood definition and if yes
	   between which compartments
	
	:Parameters:
	 - `sbmtpl` (SBMLmod) - a template of SBML as returned by lisbml
	
	:Returns:compartment,species,parameter,reaction
	 - a map of cpt name, cpt
	 - a map of species name, species
	 - a map of param name, param
	 - a map of reaction name associated to:
	     - reaction
	     - reactant compartment
	     - product compartment
	     - modifier compartment
	     - a local map giving the compartment of each element defined 
	       in this reaction
	
	:Returns type:
	 - dict of str|Compartment
	 - dict of str|Reaction
	 - dict of str|Parameter
	 - dict of str|(Reaction,str,str,str,dict of str|str)
	"""
	#compartments
	compartment = dict( (cpt.getId(),cpt) \
	                    for cpt in sbmtpl.getListOfCompartments() \
	                    if cpt.getId() != "neighbor")
	
	#species
	species = dict( (sp.getId(),sp) \
	                 for sp in sbmtpl.getListOfSpecies() )
	
	#global parameters
	parameter = dict( (param.getId(),param) \
	                   for param in sbmtpl.getListOfParameters() )
	
	#reactions analysis
	reaction = {}
	
	for reac in sbmtpl.getListOfReactions() :
		lcpt = {} #map that associate every localy defined element
		          #to a given compartment if possible or None if not
		
		#reactants compartment
		R_cpts = set()
		for sp in reac.getListOfReactants() :
			spname = sp.getSpecies()
			cpt = species[spname].getCompartment()
			R_cpts.add(cpt)
			lcpt[spname] = cpt
		
		if len(R_cpts) == 0 :
			R_cpt = None
		else :
			R_cpt, = R_cpts
		
		#products compartment
		P_cpts = set()
		for sp in reac.getListOfProducts() :
			spname = sp.getSpecies()
			cpt = species[spname].getCompartment()
			P_cpts.add(cpt)
			lcpt[spname] = cpt
		
		if len(P_cpts) == 0 :
			P_cpt = None
		else :
			P_cpt, = P_cpts
		
		#modifiers compartment
		for sp in reac.getListOfModifiers() :
			spname = sp.getSpecies()
			cpt = species[spname].getCompartment()
			lcpt[spname] = cpt
		
		#compare R and P
		if R_cpt is None or R_cpt == P_cpt :
			R_cpt = P_cpt
			P_cpt = None
		
		if P_cpt is None :
			######
			#
			#reaction occurs in a single compartment
			#
			######
			L_cpt = None
			k = reac.getKineticLaw()
			
			#find compartment of parameters locally defined
			for param in k.getListOfParameters() :
				param = param.getId()
				cpt = _param_cpt(param,compartment)
				if cpt is None :
					cpt = R_cpt
				
				lcpt[param] = cpt
			
			#analyse formula to find globally defined parameters
			for name in variables(k.getMath() ) :
				if name not in lcpt :
					if name in parameter :
						lcpt[name] = None
					else :
						msg = "parameter %s is defined nowhere" % name
						raise UserWarning(msg)
		else :
			######
			#
			#transport reaction between two compartments
			#
			######
			k = reac.getKineticLaw()
			
			#find compartment of parameters locally defined
			for param in k.getListOfParameters() :
				param = param.getId()
				cpt = _param_cpt(param,compartment)
				if cpt is None :
					msg = "Unable to find in which compartment " \
					    + "param %s is defined" % param
					raise UserWarning(msg)
				
				lcpt[param] = cpt
			
			#analyse formula to find globally defined parameters
			L_cpts = set()
			for name in variables(k.getMath() ) :
				if name in lcpt :
					L_cpts.add(lcpt[name])
				else :
					if name in parameter :
						lcpt[name] = None
					else :
						msg = "parameter %s is defined nowhere" % name
						raise UserWarning(msg)
			
			#find compartment of link element
			L_cpts -= R_cpts
			L_cpts -= P_cpts
			if len(L_cpts) == 0 :
				L_cpt = None
			else :
				L_cpt, = L_cpts
		
		#fill reaction dictionary
		reaction[reac.getId()] = (reac,R_cpt,P_cpt,L_cpt,lcpt)
	
	#return
	return compartment,species,parameter,reaction

def info (sbmtpl) :
	"""Print informations on a template
	
	These informations are intended to be used to know if a given tissue
	can be used to project the template.
	
	:Parameters:
	 - `sbmtpl` (SBMLmod) - a template of SBML as returned by lisbml
	"""
	compartment,species,parameter,reaction = analyse(sbmtpl)
	
	#cpts
	print "Tissue must contains these compartments:"
	for cpt in compartment :
		print "    - ",cpt
	
	#species
	sps = dict( (cpt,[]) for cpt in compartment)
	for name,sp in species.iteritems() :
		cpt = sp.getCompartment()
		if cpt != "neighbor" :
			sps[cpt].append( (name,sp.getSpeciesType() ) )
	
	print "These species must be defined"
	for cpt,sp_list in sps.iteritems() :
		print "in",cpt
		for sp,sptyp in sp_list :
			print "    - ",sp,
			if sptyp == "" :
				print
			else :
				print "(type: %s)" % sptyp
	
	#parameters
	if len(parameter) > 0 :
		print "These parameters must be defined uniformly accross the tissue:"
		for param in parameter :
			print "    - ",param
	
	lparam = set()
	for name,(reac,R_cpt,P_cpt,L_cpt,lcpt) in reaction.iteritems() :
		k = reac.getKineticLaw()
		for param in k.getListOfParameters() :
			param = param.getId()
			lparam.add( (param,lcpt[param]) )
	
	print "These parameters must be " \
	    + "redefined for each compartment of the tissue:"
	for name,cpt in lparam :
		print "    - %s in %s" % (name,cpt)
	
	#topological links
	if any(val[2] is not None for val in reaction.itervalues() ) :
		print "The tissue requires some kind of topological links:"
		for name,(reac,R_cpt,P_cpt,L_cpt,lcpt) in reaction.iteritems() :
			if P_cpt is not None :
				print "    - between :"
				print "         elements of type %s" % R_cpt
				print "         and",
				if P_cpt == "neighbor" :
					print "neighbor",
					P_cpt = R_cpt
				print "elements of type %s" % P_cpt
				if L_cpt is not None :
					print "         using elements of type %s as links" % L_cpt
