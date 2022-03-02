from openalea.deploy import execfile_partial

execfile_partial(vars(),"simu.py",None,"#end create field")

################################################
#
print "draw"
#
################################################
from math import pi,sin,cos
from vplants.plantgl.scenegraph import Material,Shape,\
                                       NurbsPatch
from openalea.pglviewer import SceneView

angles = [2 * pi * i / 10. for i in xrange(11)]
mat = [[(pt[0] * cos(a),pt[0] * sin(a),pt[2],pt[3]) for pt in ctrl_pts] for a in angles]

patch = NurbsPatch(mat)

sc = SceneView()
sc.set_display_mode(sc.DISPLAY.WIREFRAME)
sc.add(Shape(patch,Material( (0,0,255) ) ) )

################################################
#
print "display"
#
################################################
from openalea.pglviewer import QApplication,Viewer,View3DGUI

qapp = QApplication([])
v = Viewer()
v.add_world(sc)
v.add_gui(View3DGUI() )

v.show()
v.view().show_entire_world()

qapp.exec_()

