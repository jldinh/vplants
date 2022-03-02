####################################
#
print "read tissue"
#
#####################################
from openalea.celltissue import TissueDB

db = TissueDB()
db.read("yassin_grid.zip")

graph = db.get_topology("cc_graph")
L1 = db.get_property("L1")
STEM,d = f.read("pattern_STEM")

Y1 =   ?      
Y2 =   ?
#####################################
#
print "defines physio"
#
#####################################
from yassin import reprModel

class Param (object) :
    pass

param = Param()
param.y_2T = 1

def physio ():
    repr_model(graph,props,params)

######################################
#
print "display"
#
######################################

######################################
#
print "launch"
#
######################################