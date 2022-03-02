import sys

filename = sys.argv[1]

############################################
#
print "read template"
#
############################################
from openalea.spatialsbml import readSBML

tpl_doc = readSBML(filename)
tpl_model = tpl_doc.getModel()

############################################
#
print "read tissue"
#
############################################
from openalea.celltissue import TissueDB

db = TissueDB()
db.read("tissue.zip")

############################################
#
print "project template"
#
############################################
from openalea.spatialsbml import project,writeSBML,SBMLDocument,summary

model = project(db,tpl_model)
summary(model)

doc = SBMLDocument(model.getLevel(),model.getVersion() )
doc.setModel(model)

writeSBML(doc,"proj.sbml")

