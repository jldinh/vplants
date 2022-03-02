from time import time
from physics.electricity import WireNet
from root import herringbone2D
from physics.gui import QApplication,Viewer,Animation,Stage,\
				draw_graph2D,JetMap

g,pos,pivot,sol=herringbone2D(10,4,5,3)
print len(g)
K=dict( (eid,0.8) for eid in g.edges() )
for vid in sol :
	eid,=g.edges(vid)
	K[eid]=1e-3
fp=dict( (vid,0.) for vid in sol )
fp[pivot[0]]=1.
algo=WireNet(g,K,fp)
tinit=time()
psi=algo.potentials()
print time()-tinit

st=Stage()
draw_graph2D(st,g,pos,psi,JetMap())

qapp=QApplication([])
v=Viewer(locals())
v.set_scene(st)
v.show()
v.set_2D()
qapp.exec_()
