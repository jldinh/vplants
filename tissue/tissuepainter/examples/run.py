from openalea.pglviewer import QApplication,Viewer, ViewerGUI
from openalea.tissuepainter import TissueView, TissuepainterGUI

tv = TissueView()

qapp = QApplication([])
v = Viewer()
v.set_world(tv)
v.add_gui(ViewerGUI(vars() ) )
#v.add_gui(TissuepainterGUI(mv))
v.show()
v.view().show_entire_world()
qapp.exec_()

