import matplotlib
matplotlib.use('Qt4Agg')
import pylab
from pglviewer import QApplication,Viewer
from pglviewer.data import RangeLoop,RangeLoopGUI
from celltissue import open_tissue
from physics.chemistry import Reaction
from display import Root2DView,RootGUI
from root import Root
from simu import initialise,diffuse_auxin,transport_auxin,Phi

f=open_tissue("digit root/mockup02_shortcapped",'r')
t,pos,info=f.read()
pumps=f.read_property("pumps")
f.close()
dt=1.
r=Root(t,pos)
r.pumps=pumps
rv=Root2DView(r)
rgui=RootGUI(rv)

r.aux_plot={}
r.flux_plot={}
r.time_plot=[]


class Simu (RangeLoop) :
	def __init__ (self) :
		times=[i*dt for i in xrange(10000)]
		RangeLoop.__init__(self,times)
	def reset (self) :
		RangeLoop.reset(self)
		initialise(r)
		rv.redraw()
	def next (self) :
		time=RangeLoop.next(self)
		diffuse_auxin(r,dt)
		transport_auxin(r,dt)
		if r.autoamplified_pumps :
		   flux=dict( (eid,r.transport.flux(eid)) for eid in r.wallgraph.edges() )
		   pumpdynamic=Reaction(Phi(r.wallgraph,r.pump_creation,flux,r.alpha,r.xi),r.pump_decay)
		   pumpdynamic.react(r.eP,dt)
                rv.redraw()
                r.time_plot.append(time)
		#auxin content visualisation
		if len(r.aux_plot) != 0 :
		   pylab.clf()
		   for cid in r.aux_plot :
		       if len(r.aux_plot[cid]) == 0:
		       	  fill = [None for i in r.time_plot[1:]]
		       	  r.aux_plot[cid].extend(fill)
		       r.aux_plot[cid].append( r.auxin[cid] )
     		       pylab.plot(r.time_plot,r.aux_plot[cid])
		   pylab.ylim(0.,1.)
		   pylab.xlim(r.time_plot[0],1000*dt)
		   pylab.show()
		#auxin flux visualisation
		if len(r.flux_plot) != 0 :
		   pylab.clf()
		   for eid in r.flux_plot :
		       if len(r.flux_plot[eid]) == 0:
		       	  fill = [None for i in r.time_plot[1:]]
		       	  r.flux_plot[eid].extend(fill)
		       r.flux_plot[eid].append( r.transport.flux(eid) )
     		       pylab.plot(r.time_plot,r.flux_plot[eid])
		   pylab.ylim(0.,100.)
		   pylab.xlim(r.time_plot[0],1000*dt)
		   pylab.show()

		return time

simu=RangeLoopGUI(Simu())

qapp=QApplication([])
v=Viewer(locals())
v.set_world(rgui)
v.set_loop(simu)
v.show()
#v.view().show_entire_world()
v.set_2D()
qapp.exec_()

