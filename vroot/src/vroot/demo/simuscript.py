import matplotlib
matplotlib.use('Qt4Agg')
import pylab
from pglviewer import QApplication,Viewer
from pglviewer.data import RangeLoop,RangeLoopGUI
from physics.chemistry import Reaction
from display import Root2DView,RootGUI
from methods import prograde_auxin,diffuse_auxin,transport_auxin,Zeta,Yota,fix_eP,orient_flux,cap_auxin
from initialize import initialize

r = initialize(0)
rv=Root2DView(r)
rgui=RootGUI(rv)

class Simu (RangeLoop) :

	def __init__ (self) :
		times=[i*r.dt for i in xrange(r.timerange)]
		RangeLoop.__init__(self,times)

	def reset (self) :
		RangeLoop.reset(self)
		initialize(r)
		rv.redraw()

	def next (self) :
		time=RangeLoop.next(self)
		prograde_auxin(r,r.dt)
		diffuse_auxin(r,r.dt)
		transport_auxin(r,r.dt)
		if r.autoamplified_pumps :
		   aux_grad = dict( (eid,(r.auxin[eid[0]],r.auxin[eid[1]])) for eid in r.wallgraph.edges() )
		   pumpdynamic = Reaction(Zeta(r.pump_creation,aux_grad,r.alpha,r.zeta),Yota(r.pump_decay,aux_grad,r.beta,r.yota))
		   pumpdynamic.react(r.eP,r.dt)
                ###
                #   orient the flux toward one side only
                #
                if time == 100*r.dt :
                   orient_flux(r,0)
                if time == 300*r.dt :
                   orient_flux(r,1)
                if time == 500*r.dt :
                   orient_flux(r,0)
                fix_eP(r)
                cap_auxin(r)
                rv.redraw()
                r.time_plot.append(time)
		#auxin content visualisation
		if len(r.aux_plot) != 0 :
		   pylab.clf()
		   for cid in r.aux_plot :
		       if len(r.aux_plot[cid]) == 0:
		       	  fill = [0 for i in r.time_plot[1:]]
		       	  r.aux_plot[cid].extend(fill)
		       r.aux_plot[cid].append( r.auxin[cid] )
     		       pylab.plot(r.time_plot,r.aux_plot[cid])
		   pylab.ylim(0.,1.)
		   pylab.xlim(r.time_plot[0],1000*r.dt)
		   pylab.show()
		#auxin flux visualisation
		if len(r.flux_plot) != 0 :
		   pylab.clf()
		   for eid in r.flux_plot :
		       if len(r.flux_plot[eid]) == 0:
		       	  fill = [0 for i in r.time_plot[1:]]
		       	  r.flux_plot[eid].extend(fill)
		       r.flux_plot[eid].append( r.transport.flux(eid) )
     		       pylab.plot(r.time_plot,r.flux_plot[eid])
		   pylab.ylim(0.,100.)
		   pylab.xlim(r.time_plot[0],1000*r.dt)
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


