from openalea.pglviewer import QApplication,Viewer,Vec
from openalea.pglviewer.data import ClippingProbeView,ClippingProbeGUI
from openalea.tissuepainter import MeshView,TissuepainterGUI

mv = MeshView()
pb = ClippingProbeView(mv,size=1)
pb.set_visible(False)

qapp = QApplication([])
v = Viewer(vars())
v.set_world(mv)
gui = TissuepainterGUI(mv)
v.add_gui(gui)
#v.add_gui(ClippingProbeGUI(pb))

gui.open_tissue("vtissue.zip")
"""bb = mv.bounding_box()
R = max(bb.getSize()) #assume z axis smaller than the others
pb._size = R
cent = Vec(*tuple(bb.getCenter()))
pb.set_position(cent)"""

v.show()
v.view().show_entire_world()
qapp.exec_()

