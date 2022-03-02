level = 2
version = 4

#######################################
#
print "create document"
#
#######################################
from libsbml import SBMLDocument

doc = SBMLDocument(level,version)
model = doc.createModel("AtoB")

#######################################
#
print "create compartment"
#
#######################################
cpt = model.createCompartment()
cpt.setId("cortex")

cpt = model.createCompartment()
cpt.setId("endoderme")

cpt = model.createCompartment()
cpt.setId("wall")

cpt = model.createCompartment()
cpt.setId("neighbor")

#######################################
#
print "create species"
#
#######################################
#types
A = model.createSpeciesType()
A.setId("A")

#species
sp = model.createSpecies()
sp.setId("A_cortex")
sp.setName("A")
sp.setSpeciesType("A")
sp.setCompartment("cortex")

sp = model.createSpecies()
sp.setId("A_endoderme")
sp.setName("A")
sp.setSpeciesType("A")
sp.setCompartment("endoderme")

sp = model.createSpecies()
sp.setId("A_neighbor")
sp.setName("A")
sp.setSpeciesType("A")
sp.setCompartment("neighbor")

sp = model.createSpecies()
sp.setId("B")
sp.setCompartment("endoderme")

sp = model.createSpecies()
sp.setId("PIN")
sp.setCompartment("wall")

#######################################
#
print "create reactions"
#
#######################################
from libsbml import parseFormula

#global parameter gamma
param = model.createParameter()
param.setId("gamma")
param.setValue(1.08)

param = model.createParameter()
param.setId("delta")
param.setValue(1.12)

#creation
reac = model.createReaction()
reac.setId("creation")

sp = reac.createProduct()
sp.setSpecies("B")
sp.setStoichiometry(1)

k = reac.createKineticLaw()
alpha = k.createParameter()
alpha.setId("alpha")
alpha.setValue(3.14)
k.addParameter(alpha)

formula = parseFormula("alpha")
k.setMath(formula)

#decay
reac = model.createReaction()
reac.setId("decay")

sp = reac.createReactant()
sp.setSpecies("B")
sp.setStoichiometry(1)

k = reac.createKineticLaw()
beta = k.createParameter()
beta.setId("beta")
beta.setValue(3.14)

formula = parseFormula("beta * B")
k.setMath(formula)

#transformation
reac = model.createReaction()
reac.setId("transformation")

sp = reac.createReactant()
sp.setSpecies("B")
sp.setStoichiometry(1)

sp = reac.createProduct()
sp.setSpecies("A_endoderme")
sp.setStoichiometry(1)

k = reac.createKineticLaw()
param = k.createParameter()
param.setId("delta")

formula = parseFormula("delta * B")
k.setMath(formula)

#transport
reac = model.createReaction()
reac.setId("transport")

sp = reac.createReactant()
sp.setSpecies("A_endoderme")
sp.setStoichiometry(1)

sp = reac.createProduct()
sp.setSpecies("A_cortex")
sp.setStoichiometry(1)

sp = reac.createModifier()
sp.setSpecies("PIN")

k = reac.createKineticLaw()

formula = parseFormula("gamma * PIN * A_endoderme")
k.setMath(formula)

#diffusion
reac = model.createReaction()
reac.setId("diffusion")

sp = reac.createReactant()
sp.setSpecies("A_cortex")
sp.setStoichiometry(1)

sp = reac.createProduct()
sp.setSpecies("A_neighbor")
sp.setStoichiometry(1)

k = reac.createKineticLaw()
param = k.createParameter()
param.setId("S_wall")
param.setName("S")

formula = parseFormula("delta * S_wall * A_cortex")
k.setMath(formula)


#######################################
#
print "test"
#
#######################################
from openalea.spatialsbml import summary

summary(model)

#######################################
#
print "write template"
#
#######################################
from libsbml import writeSBML

writeSBML(doc,"complex.tpl.sbml")

