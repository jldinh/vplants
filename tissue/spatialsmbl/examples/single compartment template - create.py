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
cyto = model.createCompartment()
cyto.setId("cytoplasm")

#######################################
#
print "create species"
#
#######################################
#types
A = model.createSpeciesType()
A.setId("A")

#species
A_cyto = model.createSpecies()
A_cyto.setId("A_cytoplasm")
A_cyto.setSpeciesType("A")
A_cyto.setCompartment("cytoplasm")

B_cyto = model.createSpecies()
B_cyto.setId("B")
B_cyto.setCompartment("cytoplasm")

#######################################
#
print "create reactions"
#
#######################################
from libsbml import parseFormula

#global parameter beta
param = model.createParameter()
param.setId("gamma")
param.setValue(1.08)

#creation
creation = model.createReaction()
creation.setId("creation")

sp = creation.createProduct()
sp.setSpecies("A_cytoplasm")
sp.setStoichiometry(1)

k = creation.createKineticLaw()
alpha = k.createParameter()
alpha.setId("alpha")
alpha.setValue(3.14)
k.addParameter(alpha)

formula = parseFormula("alpha")
k.setMath(formula)

#decay
decay = model.createReaction()
decay.setId("decay")

sp = decay.createReactant()
sp.setSpecies("B")
sp.setStoichiometry(1)

k = decay.createKineticLaw()
beta = k.createParameter()
beta.setId("beta")
beta.setValue(3.14)

formula = parseFormula("beta * B")
k.setMath(formula)

#transformation
transfo = model.createReaction()
transfo.setId("transformation")

sp = transfo.createReactant()
sp.setSpecies("A_cytoplasm")
sp.setStoichiometry(1)

sp = transfo.createProduct()
sp.setSpecies("B")
sp.setStoichiometry(1)

k = transfo.createKineticLaw()

formula = parseFormula("gamma * A_cytoplasm")
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

writeSBML(doc,"Acyto_to_Bcyto.tpl.sbml")

