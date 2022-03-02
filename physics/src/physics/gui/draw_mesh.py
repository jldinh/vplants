from openalea.plantgl.scenegraph import FaceSet,Shape,Material

up=(0,0,1)

def draw_mesh2D (stage, mesh, face_property=None, colormap=None) :
	point_list=[]
	tr_pts={}
	for pid,vec in mesh.positions() :
		tr_pts[pid]=len(point_list)
		point_list.append( (vec.x,vec.y,0.) )
	index_list=[]
	tr_faces={}
	for fid in mesh.faces() :
		tr_faces[fid]=len(index_list)
		index_list.append( tuple(tr_pts[pid] for pid in mesh.points(fid=fid)) )
	geom=FaceSet(point_list,index_list)
	geom.normalList=[up]*len(index_list)
	geom.normalPerVertex=False
	if face_property is not None :
		geom.colorPerVertex=False
		geom.colorList=[ colormap(face_property[fid]).i4tuple() \
					for fid in tr_faces ]
	stage+=Shape(geom,Material( (0,0,0) ))

def draw_mesh3D (stage, mesh, face_property=None, colormap=None) :
	point_list=[]
	tr_pts={}
	for pid,vec in mesh.positions() :
		tr_pts[pid]=len(point_list)
		point_list.append( (vec.x,vec.y,vec.z) )
	index_list=[]
	tr_faces={}
	for fid in mesh.faces() :
		tr_faces[fid]=len(index_list)
		index_list.append( tuple(tr_pts[pid] for pid in mesh.points(fid=fid)) )
	geom=FaceSet(point_list,index_list)
	if face_property is not None :
		geom.colorPerVertex=False
		geom.colorList=[ colormap(face_property[fid]).i4tuple() \
					for fid in tr_faces ]
	stage+=Shape(geom,Material( (0,0,0) ))
