from math import atan2,pi,degrees
from openalea.svgdraw import open_svg,SVGSphere,SVGConnector,Vector3
from openalea.container import Graph
from root import Root

def angle (vec1, vec2) :
	a=atan2((vec1^vec2)[2],vec1*vec2)
	if a<0 :
		a+=2*pi
	return a

def create_tissue (filename) :
	f=open_svg(filename)
	sc=f.read()
	f.close()
	root=Root()
	tissue=root.tissue
	bkg=sc.get_by_id("background")
	bkg_im=list(bkg.elements())[0]
	dx=float(bkg_im.attribute("dx"))
	dy=float(bkg_im.attribute("dy"))
	layer=sc.get_by_id("cells")
	cell={}
	cell_center={}
	for elm in layer.elements() :
		cid=tissue.add_element(root.CELL)
		cell[elm.id()]=cid
		cell_center[cid]=elm.center()
	layer=sc.get_by_id("walls")
	wall={}
	for elm in layer.elements() :
		wall[elm.id()]=tissue.add_element(root.WALL)
	layer=sc.get_by_id("vertices")
	corner={}
	pos=root.position
	for elm in layer.elements() :
		pid=tissue.add_element(root.CORNER)
		corner[elm.id()]=pid
		pos[pid]=elm.center()
	layer=sc.get_by_id("wall corners")
	wall_corners=dict( (elmid,[]) for elmid in wall )
	for elm in layer.elements() :
		wid=elm.source()
		pid=elm.target()
		wall_corners[wid].append(pid)
	graph=root.corner_graph()
	for wid,(pid1,pid2) in wall_corners.iteritems() :
		graph.add_edge(corner[pid1],corner[pid2],wall[wid])
	layer=sc.get_by_id("cell corners")
	cell_corners=dict( (cid,[]) for cid in root.cells() )
	for elm in layer.elements() :
		cid=cell[elm.source()]
		pid=corner[elm.target()]
		cell_corners[cid].append(pid)
	pos=root.position
	#orienter les coins
	for cid,pid_list in cell_corners.iteritems() :
		cent=cell_center[cid]
		cent=sum((pos[pid] for pid in pid_list),Vector3())/len(pid_list)
		pidref=pid_list.pop(0)
		vref=pos[pidref]-cent
		angles=[ (angle(vref,pos[pid]-cent),pid) for pid in pid_list]
		angles.sort()
		if cid==37 :
			print [degrees(a) for a,pid in angles]
		root.cell_corners[cid]=[pidref]+[pid for a,pid in angles]
	#GRAPH de diffusion et de transport
	corners_cell=dict( (pid,set()) for pid in root.corners() )
	for cid in root.cells() :
		for pid in root.cell_corners[cid] :
			corners_cell[pid].add(cid)
	graph=root.corner_graph()
	dg=root.diffusion_graph()
	tg=root.transport_graph()
	wpr=tissue.relation(root.pump_wall_rel_id)
	for wid in list(root.walls()) :
		cells=corners_cell[graph.source(wid)]&corners_cell[graph.target(wid)]
		if len(cells)==2 :
			cid1,cid2=cells
			dg.add_edge(cid1,cid2,wid)
			pump_id=tg.add_edge(cid1,cid2)
			wpr.add_link(pump_id,wid)
			pump_id=tg.add_edge(cid2,cid1)
			wpr.add_link(pump_id,wid)
	#GEOMETRY
	root.position=dict( (pid,Vector3(vec[0]*dx,vec[1]*dy,vec[2])) for pid,vec in root.position.iteritems() )
	for cid,pid_list in root.cell_corners.iteritems() :
		cent=sum((pos[pid] for pid in pid_list),Vector3())/len(pid_list)
		nb=len(pid_list)
		surf=0.
		for i in xrange(nb) :
			surf+=((pos[pid_list[i]]-cent)^(pos[pid_list[(i+1)%nb]]-cent))[2]
		root.cell_volume[cid]=surf/2.
	graph=root.corner_graph()
	for wid in root.walls() :
		surf=(pos[graph.target(wid)]-pos[graph.source(wid)]).__norm__()
		root.wall_surface[wid]=surf
	#PHYSIO
	for cid in root.cells() :
		root.auxin[cid]=0.
		root.auxin_creation[cid]=0.
		root.auxin_degradation[cid]=0.
	graph=root.diffusion_graph()
	for eid in graph.edges() :
		root.diffusion_coeff[eid]=0.
	graph=root.transport_graph()
	for eid in graph.edges() :
		root.relative_pumps[eid]=0.
	layer=sc.get_by_id("PIN")
	graph=root.transport_graph()
	for elm in layer.elements() :
		wid=elm.target()
		pt1,pt2=elm.polyline_ctrl_points()
		pts=Vector3(*pt1)
		pte=Vector3(*pt2)
		pump1,pump2=root.associated_pumps(wall[wid])
		cids=graph.source(pump1)
		cidt=graph.target(pump1)
		#if (pts-cell_center[cids]).__normSquared__() < (pte-cell_center[cidt]).__normSquared__() :
		if (pte-pts)*(cell_center[cidt]-cell_center[cids])>0 :
			root.relative_pumps[pump1]=1.
		else :
			root.relative_pumps[pump2]=1.
	return root

