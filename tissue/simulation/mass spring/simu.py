# -*- python -*-
#
#       simulation.mass spring: test of mechanical equilibrium using mass spring
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
This module launch the simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

###################################################
#
#	create set of springs
#
###################################################
from vplants.plantgl.math import Vector2
from openalea.physics.mechanics import LinearSpring2D
NB = 10 #number of springs
l0 = 1. #(m) rest length of springs
K = 10. #(N) relative stiffness of the springs
load = 1. #(N) force exerced at the end of the line

pos = dict( (i,Vector2(i*l0,0)) for i in xrange(NB+1))
weights = dict( (i,1.) for i in xrange(NB+1))
springs = [LinearSpring2D(i,i+1,K,l0) for i in xrange(NB)]

###################################################
#
#	mechanical algo
#
###################################################
from openalea.physics.mechanics import ForwardEuler2D
dt_meca = 0.3 #(s) dt used to reach equilibrium
			#must be smaller than sqrt(2.m.l0/K)

def bound (solver) :
	solver.set_force(0,0.,0.)
	solver.set_force(NB,solver.fx(NB)+load,solver.fy(NB))

algo = ForwardEuler2D(weights,springs,bound)

def deform (*args) :
	algo.deform(pos,dt_meca,1)

###################################################
#
#	GUI
#
###################################################
import matplotlib
matplotlib.use('Qt4Agg')
from pylab import clf,plot,show,xlim,ylim,legend
from PyQt4.QtGui import QApplication
qapp = QApplication([])

times = []
strains = [[] for i in xrange(NB)]

def register (time, *args) :
	times.append(time)
	for i,spring in enumerate(springs) :
		strains[i].append(spring.strain(pos))

def plot_curves (*args) :
	clf()
	for i,mem in enumerate(strains) :
		plot(times,mem,label="sp%d" % i)
	#legend(loc='lower right')
	show()

###################################################
#
#	simulation loop
#
###################################################
from openalea.pglviewer.data import InfiniteSimu
nb_steps = 50

simu = InfiniteSimu(0.,1)
simu.add_process(deform,"deform")
simu.add_process(register,"register")
simu.add_process(plot_curves,"plot_curves")
simu.reset()
#plot([0],[0])
#show()
def run () :
	for i in xrange(nb_steps) :
		simu.next()



