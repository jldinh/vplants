#test du fonctionnement de e0

from physics.math import X,Y,xy,zeros
from physics.mechanics import TensorMechanics2D
from test_plate import *

#calcul de e0 pour des forces donnees
F=xy(0,loading*(m.position(1)-m.position(2)).norm()/2.)
algo=TensorMechanics2D(m,
		dict( (fid,material) for fid in m.faces() ),
		dict( (fid,thickness) for fid in m.faces() ),
		dict( (fid,zeros( (2,2) )) for fid in m.faces() ),
		{1:F,2:F*2,3:F},
		[(3,X),(4,X),(5,X),(5,Y),(6,Y),(7,Y)])
d1=algo.displacement()
stress1=dict( (fid,algo.stress(fid,d1)) for fid in m.faces() )
strain1=dict( (fid,algo.strain(fid,d1)) for fid in m.faces() )

#utilisation du strain comme e0 et retrait des forces
e0=strain1
algo=TensorMechanics2D(m,
		dict( (fid,material) for fid in m.faces() ),
		dict( (fid,thickness) for fid in m.faces() ),
		e0,
		{},
		[(3,X),(4,X),(5,X),(5,Y),(6,Y),(7,Y)])
d=algo.displacement()
stress=dict( (fid,algo.stress(fid,d)) for fid in m.faces() )
strain=dict( (fid,algo.strain(fid,d)) for fid in m.faces() )

#verification
seuil=1e-9
for fid,T in stress.iteritems() :
	assert abs(T[X,X])<seuil
	assert abs(T[X,Y])<seuil
	assert abs(T[Y,X])<seuil
	assert abs(T[Y,Y]-2000.)<seuil

"""
from physics.gui import QApplication,Viewer,Stage,Animation,\
				draw_mesh2D,JetMap
qapp=QApplication([])
v=Viewer(locals())
st=Stage()
draw_mesh2D(st,m)
v.set_scene(st)
v.show()
qapp.exec_()
"""
