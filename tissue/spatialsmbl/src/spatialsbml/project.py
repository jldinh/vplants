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
This module define function to project SBML templates on a tissue
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from libsbml import Model
from analyse import analyse
from formula import replace

def _fill_reaction (reac_tpl, reac, cptid, lcpt, sp_trans) :
	"""Fill information in the newly created reaction
	
	:Parameters:
	 - `reac_tpl` - template of the reaction
	 - `reac` - the newly created reaction to fill
	 - `cptid` (dict of str|int) - map of cpt name, id of the corresponding
	                               element in the tissue
	 - `lcpt` (dict of str|str) - map of elm, corresponding compartment
	"""
	trans = {}
	#reactants
	R_cpts = set()
	for spr_tpl in reac_tpl.getListOfReactants() :
		name_tpl = spr_tpl.getSpecies()
		cpt = lcpt[name_tpl]
		R_cpts.add(cpt)
		name = "%s_%d" % (sp_trans[name_tpl],cptid[cpt])
		trans[name_tpl] = name
		
		spr = spr_tpl.clone()
		spr.setSpecies(name)
		reac.addReactant(spr)
	
	#products
	for spr_tpl in reac_tpl.getListOfProducts() :
		name_tpl = spr_tpl.getSpecies()
		cpt = lcpt[name_tpl]
		if cpt == "neighbor" :
			R_cpt, = R_cpts
			real_name = name_tpl.replace("neighbor",R_cpt)
		else :
			real_name =name_tpl
		name = "%s_%d" % (sp_trans[real_name],cptid[cpt])
		trans[name_tpl] = name
		
		spr = spr_tpl.clone()
		spr.setSpecies(name)
		reac.addProduct(spr)
	
	#modifiers
	for spr_tpl in reac_tpl.getListOfModifiers() :
		name_tpl = spr_tpl.getSpecies()
		name = "%s_%d" % (sp_trans[name_tpl],cptid[lcpt[name_tpl] ])
		trans[name_tpl] = name
		
		spr = spr_tpl.clone()
		spr.setSpecies(name)
		reac.addModifier(spr)
	
	#kinetic law
	k = reac.createKineticLaw()
	formula = reac_tpl.getKineticLaw().getMath()
	for name_tpl,name in trans.iteritems() :
		formula = replace(formula,name_tpl,name)
	
	for param_tpl in reac_tpl.getKineticLaw().getListOfParameters() :
		name_tpl = param_tpl.getId()
		name = "%s_%d" % (name_tpl,cptid[lcpt[name_tpl] ])
		
		param = param_tpl.clone()
		param.setId(name)
		k.addParameter(param)
		
		formula = replace(formula,name_tpl,name)
	
	k.setMath(formula)

def project (tissuedb, sbmtpl, elm_name = {}) :
	"""Project a template on a tissue to construct a full SB model
	
	This function takes an SBML template, parse it and try to find in the tissue
	the corresponding elements. It then construct a full SBML model including
	all the reactions defined in the template for each element of the tissue.
	
	.. seealso: :func:`analyse` to read the template beforehand and ensure that
	            the tissue match the template (e.g. elements of the tissue
	            correspond to compartements defined in the template)
	
	:Parameters:
	 - `tissuedb` (TissueDB) - the tissue on which to project the template
	                           and a set of properties
	 - `sbmtpl` (SBMLmod) - a template of SBML as returned by lisbml
	 - `elm_name` (map of elmid|str) - if given, this property must give a name
	                           to some elements in the tissue in order to bypass
	                           their type (e.g. to differentiate cells in cortex
	                           and cells in endoderme which are both cells)
	
	:Returns: an SBML model as produced by libsbml
	
	:Returns type: SBMLmodel
	"""
	tissue = tissuedb.tissue()
	
	compartment,species,parameter,reaction = analyse(sbmtpl)
	
	#########
	#
	#	test adequation between tissue and template
	#
	#########
	#test tissue compartments
	tcpt = dict( (tissue.type_name(typ),typ) for typ in tissue.types() )
	
	for cpt in compartment :
		if cpt not in tcpt :
			msg = "The tissue do not defines any compartment of type '%s'" % cpt
			raise UserWarning(msg)
	
	#test topological relations
	trel = {}
	for rid in tissue.relations() :
		rel = tissue.relation(rid)
		if rel.name == "graph" :
			vtyp,etyp = rel.involved_elements()
			key = (vtyp,vtyp)
			trel.setdefault(key,[]).append( (etyp,rid,0,True) )
		elif rel.name == "mesh" :
			typs = tuple(rel.involved_elements() )
			for i in xrange(len(typs) - 1) :
				key = (typs[i],typs[i + 1])
				trel.setdefault(key,[]).append( (None,rid,i,False) )
				
				key = (typs[i + 1],typs[i])
				trel.setdefault(key,[]).append( (None,rid,i + 1,True) )
	
	reac_rel = {}
	for name,(reac,R_cpt,P_cpt,L_cpt,lcpt) in reaction.iteritems() :
		if P_cpt is None :
			#reaction occurs in a single compartment
			pass
		else :
			#transport reaction between compartments requires topo links
			if P_cpt == "neighbor" :
				key = (tcpt[R_cpt],tcpt[R_cpt])
			else :
				key = (tcpt[R_cpt],tcpt[P_cpt])
			
			if key not in trel :
				raise UserWarning("The tissue do not defines " \
				                + "any relation between elements of type " \
				                + "%s and %s" % (R_cpt,P_cpt) )
			
			match_rel = []
			for (etyp,rid,deg,ori) in trel[key] :
				if L_cpt is None or etyp == tcpt[L_cpt] :
					match_rel.append( (rid,deg,ori) )
			
			if len(match_rel) == 0 :
				raise UserWarning("The tissue does not defines " \
				                + "any relation between elements of type " \
				                + "%s and %s" % (R_cpt,P_cpt) )
			elif len(match_rel) > 1 :
				raise UserWarning("Ambiguity, multiple relations" \
				                + "are defined between elements of type " \
				                + "%s and %s" % (R_cpt,P_cpt) )
			else :
				reac_rel[name], = match_rel
	
	#########
	#
	#	project template on tissue
	#
	#########
	#create model
	sbm = Model(sbmtpl.getLevel(),sbmtpl.getVersion() )
	sbm.setName(sbmtpl.getName() )
	
	#create compartements
	for name,cpt_tpl in compartment.iteritems() :
		#create compartment type
		cpt_typ = sbm.createCompartmentType()
		cpt_typ.setId(name)
		
		#create a compartment for each element
		#of the corresponding type in the tissue
		for elmid in tissue.elements(tcpt[name]) :
			cpt = cpt_tpl.clone()
			cpt.setId("%s_%d" % (name,elmid) )
			cpt.setCompartmentType(name)
			sbm.addCompartment(cpt)
	
	#create species
	sp_trans = {}
	for name,sp_tpl in species.iteritems() :
		cpt = sp_tpl.getCompartment()
		if cpt != "neighbor" :
			#find element type for the compartment that own the species
			typ = tcpt[cpt]
			
			#create species type
			sp_typ_name = sp_tpl.getSpeciesType()
			sp_trans[name] = name
			if sp_typ_name == "" :
				sp_typ_name = name
			elif sp_typ_name == sp_tpl.getName() :
				gr = name.split("_")
				if gr[-1] in compartment :
					new_name = "_".join(gr[:-1])
					sp_trans[name] = new_name
					name = new_name
			
			sp_typ = sbm.createSpeciesType()
			sp_typ.setId(sp_typ_name)
			
			#add species for each element
			#of the corresponding type in the tissue
			for elmid in tissue.elements(typ) :
				sp = sp_tpl.clone()
				sp.setId("%s_%d" % (name,elmid) )
				sp.setSpeciesType(sp_typ_name)
				sp.setCompartment("%s_%d" % (cpt,elmid) )
				sbm.addSpecies(sp)
	
	#create global parameters :
	for name,param in parameter.iteritems() :
		sbm.addParameter(param)
	
	#create reactions
	for name,(reac_tpl,R_cpt,P_cpt,L_cpt,lcpt) in reaction.iteritems() :
		print name,lcpt
		if P_cpt is None :
			#single compartment reactions
			
			#iterate on all compartments in the tissue of the given type
			for elmid in tissue.elements(tcpt[R_cpt]) :
				reac = sbm.createReaction()
				reac.setId("%s_%d" % (name,elmid) )
				_fill_reaction(reac_tpl,reac,{R_cpt:elmid},lcpt,sp_trans)
		else :
			#multi compartments reactions
			
			#find tissue relation
			rid,deg,direct = reac_rel[name]
			rel = tissue.relation(rid)
			
			if rel.name == "graph" :
				#iterate on all links in the relation
				for eid in rel.edges() :
					reac = sbm.createReaction()
					reac.setId("%s_%d" % (name,eid) )
					_fill_reaction (reac_tpl,
					                reac,
					                {R_cpt:rel.source(eid),
					                P_cpt:rel.target(eid),
					                L_cpt:eid},
					                lcpt,
					                sp_trans)
			elif rel.name == "mesh" :
				if ori :
					#iterate on borders of elements
					for wid in rel.wisps(deg) :
						for bid in rel.borders(deg,wid) :
							reac = sbm.createReaction()
							reac.setId("%s_%d_%d" % (name,wid,bid) )
							_fill_reaction(reac_tpl,
							               reac,
							               {R_cpt:wid,
							               P_cpt:bid},
							               lcpt,
							               sp_trans)
				else :
					#iterate on regions of elements
					for wid in rel.wisps(deg) :
						for rid in rel.regions(deg,wid) :
							reac = sbm.createReaction()
							reac.setId("%s_%d_%d" % (name,wid,rid) )
							_fill_reaction(reac_tpl,
							               reac,
							               {R_cpt:wid,
							               P_cpt:rid},
							               lcpt,
							               sp_trans)
			else :
				msg = "I do not handle that kind of relation: %s" % rel.name
				raise NotImplementedError(msg)
	
	#return
	return sbm



