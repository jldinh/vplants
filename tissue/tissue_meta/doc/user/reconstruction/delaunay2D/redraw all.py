from os import popen
from glob import glob

for filename in glob("*_draw.py") :
	popen("python %s" % filename)

