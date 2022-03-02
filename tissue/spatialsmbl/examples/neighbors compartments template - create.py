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
cpt.setId("cytoplasm")

cpt = model.createCompartment()
cpt.setId("neighbor")

cpt = model.createCompartment()
cpt.setId("wall")

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
sp.setId("A_cytoplasm")
sp.setSpeciesType("A")
sp.setCompartment("cytoplasm")

sp = model.createSpecies()
sp.setId("A_neighbor")
sp.setSpeciesType("A")
sp.setCompartment("neighbor")

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

#creation
reac = model.createReaction()
reac.setId("creation")

sp = reac.createProduct()
sp.setSpecies("A_cytoplasm")
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
sp.setSpecies("A_cytoplasm")
sp.setStoichiometry(1)

k = reac.createKineticLaw()
beta = k.createParameter()
beta.setId("beta")
beta.setValue(3.14)

formula = parseFormula("beta * A_cytoplasm")
k.setMath(formula)

#transformation
reac = model.createReaction()
reac.setId("transport")

sp = reac.createReactant()
sp.setSpecies("A_cytoplasm")
sp.setStoichiometry(1)

sp = reac.createProduct()
sp.setSpecies("A_neighbor")
sp.setStoichiometry(1)

sp = reac.createModifier()
sp.setSpecies("PIN")

k = reac.createKineticLaw()
param = k.createParameter()
param.setId("S_wall")
param.setName("S")

formula = parseFormula("gamma * S_wall * PIN * A_cytoplasm")
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

writeSBML(doc,"Acyto_to_Acyto.tpl.sbml")

