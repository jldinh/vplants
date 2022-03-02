from physics.math import zeros
from celltissue import open_tissue
from celltissue.data import PropertyMap,FactorMap,TPropertyMap,TUniformMap,TDensityMap
from celltissue.data.wisp_triangulation import WispTriangulation2D,FaceMap
from celltissue.simulation import SimuLoop,SimuLoopGUI
#locals
from meca import MecaGrowth
from physiology import Physiology
from growth import Growth
from division import CellDivision
from cell_state import CellState
from display import Redraw,Snapshot
from meristem_gui import MeristemView2D,MeristemGUI
#display
from celltissue.gui import black,blue
from celltissue.gui.pgl import TissueView2D,TissueGUI
from pglviewer import QApplication,Viewer
from pglviewer.data import GroupGUI,RangeLoop,RangeLoopGUI

f=open_tissue("mockup",'r')
t,pos,info=f.read()
f.close()
pos_init=dict( (pid,v.copy()) for pid,v in pos.iteritems() )
Vmoy=sum(t.geometry(0,cid).volume(pos) for cid in t.wisps(0))/t.nb_wisps(0)

wt=WispTriangulation2D(0,t,pos)
thickness=TUniformMap(0,t,info["tissue thickness"])
###############################
#
#	physio
#
###############################
D=TDensityMap(TUniformMap(1,t,info["D"]),t,wt)
Brel=TPropertyMap(0,0.,((cid,1.) for cid in t.wisps(0)))
B=FactorMap(Brel,info["decay"])

fixed_conc=TPropertyMap(0,0.)

IAArel=TDensityMap(TPropertyMap(0,0.,( (wid,0.5) for wid in t.wisps(0))),t,wt)
IAA=FactorMap(IAArel,1.)

physio=Physiology(t,wt,D.as_quantity(),B,fixed_conc,IAA)
###############################
#
#	mecanique
#
###############################
P=info["P"]*2.
fixed=info["fixed"]
nu=info["nu"]
Erel=TPropertyMap(0,0.,((cid,1.) for cid in t.wisps(0)))
E=FactorMap(Erel,info["E"])

Grel=TPropertyMap(0,0.,((cid,1.) for cid in t.wisps(0)))
G=FactorMap(Grel,0.5)
Gth=0.2
strain0=FaceMap(wt)
for fid in wt.faces() :
	strain0[fid]=zeros( (2,2) )

meca=MecaGrowth(wt,thickness,P,fixed,nu,E,G,Gth,strain0)

##############################
#
#		display
#
##############################
f=open_tissue("mockup",'r')
t_init,pos_init,info_init=f.read()
f.close()
tv_init=TissueView2D(t_init,pos_init)
tv_init.display_wisp(1,True)
tv_init.set_wisp_color(1,black)
tv_init.redraw()

mv=MeristemView2D(t,wt,IAArel,physio,meca)
mv.display_wisp(1,True)
mv.set_wisp_color(1,black)
mv.redraw()

##############################
#
#		processes
#
##############################
qapp=QApplication([])
g=GroupGUI()
v=Viewer(locals())
v.set_world(g)

Vref=Vmoy*1.3
print Vref
div=CellDivision(t,wt,Vref,(Brel,fixed_conc,IAArel,Erel,Grel,strain0))
growth=Growth(wt,meca,(IAArel,))
cell_state=CellState(IAArel,Grel)
redraw=Redraw(mv)
snapshot=Snapshot(v.view())
##############################
#
#		simulation
#
##############################
time_step=1.
times=[i*time_step for i in xrange(10000)]
plist=[div,cell_state,physio,growth,redraw,snapshot]
simu=SimuLoop(plist,times)
simu.enable_process(5,False)
simu.run_processes(1e-6)
test_strain=[meca.turgor_strain(wid).trace() for wid in t.wisps(0)]
mv._strain_min=min(test_strain)/1.5
mv._strain_max=max(test_strain)*1.1

g.add(TissueGUI(tv_init))
g.add(MeristemGUI(mv))
g.set_current_element(0)
g.set_visible(False)
g.set_current_element(1)
v.set_loop(SimuLoopGUI(simu))
v.set_2D()
v.show()
qapp.exec_()
