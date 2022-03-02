from openalea.container.graph import Graph
from physics.math import xy

def herringbone2D (order0_length, order0_node_size, order1_length, order1_node_size) :
	pivot_incr=xy(0,-1)
	ramif_incr=xy(1,0)
	sol_incr=xy(1,-1)
	ramif_incr2=xy(-1,0)
	sol_incr2=xy(-1,-1)
	g=Graph()
	pos={}
	sol=[]
	collar=g.add_vertex()
	pos[collar]=xy()
	pivot=[collar]
	for i in xrange(order0_length-1) :
		fid=pivot[-1]
		#entrenoeud du pivot
		for j in xrange(order0_node_size) :
			vid=g.add_vertex()
			pivot.append(vid)
			eid=g.add_edge( (fid,vid) )
			pos[vid]=pos[fid]+pivot_incr
			#noeud sol
			sid=g.add_vertex()
			sol.append(sid)
			eid=g.add_edge( (vid,sid) )
			pos[sid]=pos[vid]+sol_incr
			fid=vid
		#ramif1
		for j in xrange(order1_length) :
			for k in xrange(order1_node_size) :
				vid=g.add_vertex()
				eid=g.add_edge( (fid,vid) )
				pos[vid]=pos[fid]+ramif_incr
				fid=vid
				#noeud sol
				sid=g.add_vertex()
				sol.append(sid)
				eid=g.add_edge( (vid,sid) )
				pos[sid]=pos[vid]+sol_incr
		#ramif2
		fid=pivot[-1]
		for j in xrange(order1_length) :
			for k in xrange(order1_node_size) :
				vid=g.add_vertex()
				eid=g.add_edge( (fid,vid) )
				pos[vid]=pos[fid]+ramif_incr2
				fid=vid
				#noeud sol
				sid=g.add_vertex()
				sol.append(sid)
				eid=g.add_edge( (vid,sid) )
				pos[sid]=pos[vid]+sol_incr2
	#last entrenoeud
	fid=pivot[-1]
	for j in xrange(order0_node_size) :
		vid=g.add_vertex()
		pivot.append(vid)
		eid=g.add_edge( (fid,vid) )
		pos[vid]=pos[fid]+pivot_incr
		fid=vid
		#noeud sol
		sid=g.add_vertex()
		sol.append(sid)
		eid=g.add_edge( (vid,sid) )
		pos[sid]=pos[vid]+sol_incr
	return g,pos,pivot,sol
