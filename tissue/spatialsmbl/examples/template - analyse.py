import sys

filename = sys.argv[1]
print "####################################################"
print "####################################################"
print "####################################################"
print filename
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
print "analyse template"
#
############################################
from openalea.spatialsbml import summary,analyse,info

summary(tpl_model)

ret = analyse(tpl_model)

#for inf in ret :
#	print inf

print "####################################################"
info(tpl_model)

