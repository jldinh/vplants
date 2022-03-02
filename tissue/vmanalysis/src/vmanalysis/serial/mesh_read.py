from openalea.container import Topomesh
import raw_read

def read (filename) :
	file_descr=raw_read.read(filename)
	dimX,dimY,dimZ,vX,vY,vZ=file_descr[-1]
	scale=(vX,vY,vZ)
	m=Topomesh(3)
	mesh_prop=[]
	prop={}
	for pid,(dum,pt_prop) in file_descr[0].iteritems() :
		m.add_wisp(0,pid)
		prop[pid]=tuple(scale[i]*pt_prop[i] for i in xrange(3))
	mesh_prop.append(prop)
	for i in xrange(1,4) :
		prop={}
		for wid,(border_list,wisp_prop) in file_descr[i].iteritems() :
			m.add_wisp(i,wid)
			prop[wid]=wisp_prop
			for bid in border_list :
				m.link(i,wid,bid)
		mesh_prop.append(prop)
	return m,mesh_prop
