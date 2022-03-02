"""Read lineage files as created by Romain Fernandez
"""

def read_lineage (filename) :
	"""Read lineage file
	
	Romain Fernandez format
	
	Return a dictionary associating
	the id of a cell in stage i with
	a list of daughter cells in stage
	i + 1
	
	:Returns Type: dict of (cid, list of cid)
	"""
	f = open(filename,'r')
	lines = f.readlines()
	f.close()
	
	#skip header
	ind = 0
	cont = True
	while cont :
		line = lines[ind]
		if ":" in line :
			try :
				cid = int(line.split(":")[0] )
				if cid > 1 :
					ind -= 1
					cont = False
			except ValueError :
				pass
		
		ind += 1
	
	lines = lines[ind:]
	
	#read lineage
	lineage = {}
	
	for line in lines :
		gr = line.split(":")
		mid = int(gr[0])
		gr = gr[1].split("->")
		dids = eval(gr[1])
		if len(dids) > 1 :
			lineage[mid] = dids[:-1] #last one is -1
	
	#return
	return lineage

def read_lineage_bis (filename) :
	"""Read lineage file
	
	Vicent Mirabet format
	
	Return a dictionary associating
	the id of a cell in stage i with
	a list of daughter cells in stage
	i + 1
	
	:Returns Type: dict of (cid, list of cid)
	"""
	lineage = {}
	
	f = open(filename,'r')
	for line in f.readlines() :
		cids = tuple(int(val) for val in line.strip().split() )
		if len(cids) > 1 :
			lineage[cids[0]] = cids[1:]
	
	f.close()
	
	#return
	return lineage

