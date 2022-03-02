from openalea import tissuedb as db

def topen (filename, mode) :
	filestream = db.topen(filename,mode)
	return filestream,
