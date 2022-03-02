# -*- python -*-
#
#       simulation.installation: installation tutorial package
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
This module test the installation of physics
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

###################################################
#
#	read tissue and properties
#
###################################################
from openalea.plantgl.math import Vector2
from openalea.physics.mechanics import LinearSpring2D,ForwardEuler2D

pos = {0:Vector2(0,0),1:Vector2(1,0)}
weight = {0:1,1:1}
spring = LinearSpring2D(0,1,2.,1.)

def bound (solver) :
	solver.set_force(0,0.,0.)
	solver.set_force(1,solver.fx(1)+1.,solver.fy(1))

algo = ForwardEuler2D(weight,[spring],bound)

for i in xrange(100) :
	algo.deform(pos,0.5,1)
	print pos[1].x



