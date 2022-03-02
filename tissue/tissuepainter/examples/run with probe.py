from openalea.pglviewer import QApplication,Viewer
from openalea.pglviewer.data import ClippingProbeView,ClippingProbeGUI
from openalea.tissuepainter import MeshView,TissuepainterGUI

mv = MeshView()
pb = ClippingProbeView(mv,size=1)

qapp = QApplication([])
v = Viewer(vars())
v.set_world(pb)
v.add_gui(TissuepainterGUI(mv))
v.add_gui(ClippingProbeGUI(pb))
v.show()
v.view().show_entire_world()
qapp.exec_()

