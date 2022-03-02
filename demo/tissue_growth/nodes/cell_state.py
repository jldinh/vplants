###################################################
#
#	cell state link physiology to mechanical parameter
#
###################################################
def link1 (morphogen, turgor) :
	"""
	link morphogen concentration to turgor pressure
	"""
	for cid,conc in morphogen.iteritems() :
		turgor[cid] = conc / 5.

def link2 (morphogen, gamma) :
	"""
	link morphogen concentration to wall synthesis rate
	"""
	for cid,conc in morphogen.iteritems() :
		gamma[cid] = conc * 2.

def link3 (morphogen, mesh, K) :
	"""
	link morphogen concentration to wall stiffness
	"""
	for wid in mesh.wisps(1) :
		nb_regions = mesh.nb_regions(1,wid)
		conc = sum(morphogen[cid] for cid in mesh.regions(1,wid)) / nb_regions
		if nb_regions == 1 :
			K[wid] = max(0.5,(1 - conc) * 2.)
		else :
			K[wid] = max(0.1,(1 - conc))

def init_cell_state (param) :
	param.cell_age = {}
	return param,

def cell_state_process1 (param) :
	def process (time, dt) :
		link1(param.morphogen,param.turgor)
	return (process,"cell_state"),

def cell_state_process2 (param) :
	def process (time, dt) :
		link2(param.morphogen,param.gamma)
	return (process,"cell_state"),

def cell_state_process3 (param) :
	def process (time, dt) :
		link3(param.morphogen,param.mesh,param.K)
	return (process,"cell_state"),

