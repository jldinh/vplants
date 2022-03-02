from os import rename
from os.path import basename,join
from glob import glob
from getpass import getpass
from openalea.misc.gforge_upload import Uploader

egg_files = glob("dist/*.egg")
if len(egg_files)!=1 :
	raise UserWarning("clean dist directory and reload setup.py")

oldname = basename(egg_files[0])

if oldname.startswith("VPlants.") :
	filename = oldname
else :
	filename = "VPlants.%s" % oldname
	rename(join("dist",oldname),
	       join("dist",filename) )
print filename

kwds = {}
kwds['project'] = "openalea"
kwds['package'] = "VPlants"
kwds['release'] = "0.7"
kwds['directory'] = "dist/"
kwds['simulate'] = False
kwds['login'] = "chopard"
kwds['password'] = getpass("password for chopard:")

#python 2.5
kwds['filename'] = filename
uploader = Uploader(**kwds)
uploader.add()
#python 2.6
filename26 = filename.replace("py2.5","py2.6")
rename(join("dist",filename),
       join("dist",filename26) )

kwds['filename'] = filename26
uploader = Uploader(**kwds)
uploader.add()

