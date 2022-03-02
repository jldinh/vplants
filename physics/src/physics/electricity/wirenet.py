try :
	from scipy import zeros,ones
	from scipy.sparse import lil_matrix as matrix
	from scipy.linsolve import spsolve as solve
except ImportError :
	print "you must install scipy to use diffusion"

class WireNet (object) :
	"""
	compute potentials inside a wirenet
	represented by a directed graph without loops
	"""
	def __init__ (self, graph, K, fixed_potentials) :
		self._graph=graph # representation of the network
		self._K=K # conductances associated with edges of the graph
		self._fixed_potentials=fixed_potentials # fixed potential in some node of the graph
	
	def opposite (self, eid, vid) :
		sid=self._graph.source(eid)
		if sid==vid :
			return self._graph.target(eid)
		else :
			return sid
	
	def potentials (self) :
		g=self._graph
		K=self._K
		fp=self._fixed_potentials
		fixed_vid=set(fp)
		free_vid=set(g.vertices())-fixed_vid
		trans=dict( (vid,ind) for ind,vid in enumerate(free_vid) )
		#fill matrices
		a=matrix( (len(free_vid),len(free_vid)) )
		b=zeros(len(trans))
		for vid,i in trans.iteritems() :
			if g.nb_edges(vid)<2 :
				raise UserWarning("you must specify potential for vertex %d" % vid)
			for eid in g.edges(vid) :
				k=K[eid]
				a[i,i]+=k
				nid=self.opposite(eid,vid)
				if nid in fixed_vid :
					b[i]+=fp[nid]*k
				else :
					a[i,trans[nid]]=-k
		#resolution du systeme
		res=solve(a,b)
		pot=dict( (vid,float(res[i])) for vid,i in trans.iteritems() )
		for vid,psi in fp.iteritems() :
			pot[vid]=psi
		return pot
	
	def flux (self, eid, potentials) :
		sid=self._graph.source(eid)
		tid=self._graph.target(eid)
		return self._K[eid]*(potentials[tid]-potentials[sid])
