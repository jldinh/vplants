# -*- python -*-
#
#       tissuepainter: application to visualize and manipulate tissues
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
This module defines the gui of a simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from time import time
from openalea.pglviewer import QApplication,Viewer,Vec, \
                               ViewerGUI, \
                               ClippingProbeView,ClippingProbeGUI
from mesh_view import MeshView
from tissuepainter_gui import TissuepainterGUI

def launch (filename = None, probe = False) :
	"""
	launch a tissue painter
	if filename is given open it
	if probe is True, add a clipping probe to the view
	"""
	mv = MeshView()
	if probe :
		pb = ClippingProbeView(mv,size=1)
		pb.set_visible(False)
	
	qapp = QApplication.instance()
	if qapp is None :
		qapp = QApplication([])
	v = Viewer()
	if probe :
		v.set_world(pb)
	else :
		v.set_world(mv)
	v.add_gui(ViewerGUI(vars() ) )
	gui = TissuepainterGUI(mv)
	v.add_gui(gui)
	if probe :
		v.add_gui(ClippingProbeGUI(pb) )
	btime = time()
	if filename is not None :
		gui.open_tissue(filename)
		mv.display_scale(0,False)
		mv.display_scale(mv._mesh.degree(),True)
		gui.ui.scale_widget.setCurrentIndex(mv._mesh.degree() )
		if probe :
			bb = mv.bounding_box()
			R = max(bb.getSize() ) #assume z axis smaller than the others
			pb._size = R
			cent = Vec(*tuple(bb.getCenter() ) )
			pb.set_position(cent)
	
	v.show()
	v.view().show_entire_world()
	print "time",time() - btime
	qapp.exec_()

