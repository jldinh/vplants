from random import random
from PyQt4.QtGui import QApplication
from openalea.simpleplot import Sequence,Plotter

seq = Sequence("time","h","s","m")
for i in xrange(100) :
	seq.add(i,random() )

qapp = QApplication([])
plt = Plotter(seq)
plt.show()
qapp.exec_()

