f=open("grapheMeristeme.txt",'r')
lines=f.readlines()
f.close()

meta_offset=15
gr=lines[meta_offset].split(":")
elem=gr[1].split(" ")
dimX=int(elem[0])
dimY=int(elem[1])
dimZ=int(elem[2])
vX=float(elem[3])
vY=float(elem[4])
vZ=float(elem[5])


cell_offset=17
nb_cells=int(lines[cell_offset][9:])
cell_prop={}
for line in lines[cell_offset+1:cell_offset+nb_cells+1] :
	gr=line.split(" ")
	cid=int(gr[0])
	vvox=int(gr[1])
	vol=float(gr[2])
	layer=int(gr[3])
	barX=float(gr[4])
	barY=float(gr[5])
	barZ=float(gr[6])
	cell_prop[cid]=(vvox,vol,layer,barX,barY,barZ)

face_offset=cell_offset+nb_cells+2
nb_faces=int(lines[face_offset][6:])
cell_face=dict( (cid,[]) for cid in cell_prop )
face_prop={}
for line in lines[face_offset+1:face_offset+nb_faces+1] :
	gr=line.replace("\n","").split(" ")
	fid,cid1,cid2=(int(val) for val in gr if len(val)>0)
	face_prop[fid]=None
	for cid in (cid1,cid2) :
		cell_face[cid].append(fid)

edge_offset=face_offset+nb_faces+2
nb_edges=int(lines[edge_offset][7:])
face_edge=dict( (fid,[]) for fid in face_prop )
edge_prop={}
for line in lines[edge_offset+1:edge_offset+nb_edges+1] :
		gr=line.split(":")
		eid=int(gr[0])
		edge_prop[eid]=None
		for val in gr[1].split(" ")[1:] :
			face_edge[int(val)].append(eid)

vertex_offset=edge_offset+nb_edges+2
nb_vertices=int(lines[vertex_offset][8:])
edge_vertex=dict( (eid,[]) for eid in edge_prop )
vertex_prop={}
for line in lines[vertex_offset+1:vertex_offset+1+nb_vertices] :
		gr=line.split(":")
		pid=int(gr[0])
		vertex_prop[pid]=tuple(float(val) for val in gr[1].split(" "))
		for val in gr[2].split(" ")[1:] :
			edge_vertex[int(val)].append(pid)

f=open("meristem_graph.txt",'w')
f.write(""" 
Fichier descripteur du complexe simplicial d'un meristeme
organisation du fichier:
Vertex:nb_vertices
pid:X Y Z

Edge:nb_edges
eid:pid list

Face:nb_faces
fid:eid list

Cell:nb_cells
cid:nb_voxels volume layer:fid list
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
""")
f.write("Image:%d %d %d %f %f %f \n--------------------------------------------------------------\n\n" % (dimX,dimY,dimZ,vX,vY,vZ))
f.write("Vertex:%d\n" % len(vertex_prop))
for pid,coords in vertex_prop.iteritems() :
	f.write("%d:%.1f %.1f %.1f\n" % tuple((pid,)+coords))

f.write("\n")
f.write("Edge:%d\n" % len(edge_prop))
for eid,prop in edge_prop.iteritems() :
	f.write("%d:" % eid)
	for pid in edge_vertex[eid] :
		f.write(" %d" % pid)
	f.write("\n")

f.write("\n")
f.write("Face:%d\n" % len(face_prop))
for fid,prop in face_prop.iteritems() :
	f.write("%d:" % fid)
	for eid in face_edge[fid] :
		f.write(" %d" % eid)
	f.write("\n")

f.write("\n")
f.write("Cell:%d\n" % len(cell_prop))
for cid,(vox,vol,lay,barX,barY,barZ) in cell_prop.iteritems() :
	f.write("%d:%d %f %d %f %f %f:" % (cid,vox,vol,lay,barX,barY,barZ))
	for fid in cell_face[cid] :
		f.write(" %d" % fid)
	f.write("\n")

f.close()
