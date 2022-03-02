import sys

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMainWindow, QPushButton
from PyQt4.Qt import Qt
from OpenGL.GL import *
from OpenGL.GLU import *

from openalea.lpy import *
from openalea.plantgl.all import *
from PyQGLViewer import *

from config import get_shared_model, get_shared_image

def make_callback(m, n, d):
    def anon(value):
        m[n] = d[value]
    return anon


class Widget(QGLViewer):

    def __init__(self, parent=None):
        QGLViewer.__init__(self, parent)
        self.scene = Scene()
        self.discretizer = Discretizer()
        self.bboxcomputer = BBoxComputer(self.discretizer)
        self.renderer = GLRenderer(self.discretizer)
        self.renderer.renderingMode = GLRenderer.Dynamic

    def setScene(self, scene):
        self.scene = scene
        self.renderer.clear()
        self.bboxcomputer.clear()
        self.scene.apply(self.bboxcomputer)
        result = self.bboxcomputer.result
#        self.setSceneBoundingBox(Vec(*result.lowerLeftCorner),Vec(*result.upperRightCorner))
        self.updateGL()

    def draw(self):
        if not self.isVisible():
            self.show()
        self.scene.apply(self.renderer)

    def plot(self, scene):
        self.setScene(scene)

    def selection(self):
        return None

    def waitSelection(self, txt):
        return None





class Demo(QMainWindow):

    def __init__(self, lsys=None, params=[], icons=[], parent=None):
        QMainWindow.__init__(self, parent)
        self.iconSize = [250,100];
        self.lsys = lsys
        self.params = params
        self.icons = icons
        self.env = {}

        self.widget = Widget()
        registerPlotter(self.widget)
        self.setCentralWidget(self.widget)

        self.layout = QtGui.QHBoxLayout()
        self.vlayout = QtGui.QVBoxLayout(self.widget)
        self.vlayout.addStretch(0)
        self.vlayout.addLayout(self.layout)

        #pm = QtGui.QPixmap('heix.png')
        self.button = QPushButton('', self.widget)
        self.button.setMinimumSize(self.iconSize[1],self.iconSize[1])
        self.button.setMaximumSize(self.iconSize[1],self.iconSize[1])
        self.button.setIcon(QtGui.QIcon(get_shared_image('GoButton.png')))
        self.button.setIconSize(QtCore.QSize(self.iconSize[1],self.iconSize[1]))
        
        #mask = pm.mask()
        mask = QtGui.QBitmap(get_shared_image('GoButtonMask.png'))
        self.button.setMask(mask);

        def buttonCallback():
            self.lsys.context().updateNamespace(self.env)
            self.lsys.animate()
        
        def printImageCB():
            self.printImage()
        
        self.add_controls()

        QtCore.QObject.connect(self.button, QtCore.SIGNAL('clicked()'), buttonCallback)
        self.layout.addStretch(0)
        self.layout.addWidget(self.button)

        self.widget.setLayout(self.vlayout)


    def add_controls(self):
        for name, vals in self.params:
            if len(vals) < 2: assert False
            elif len(vals) == 2:
                # checkbox
                checkbox = QtGui.QCheckBox(name)
                callback = make_callback(self.env, name, vals)
                QtCore.QObject.connect(checkbox,QtCore.SIGNAL("stateChanged(int)"), callback)
                self.layout.addWidget(checkbox)
            else:
                # combobox
                combo = QtGui.QComboBox()
                for x in range(len(vals)): 
                    combo.addItem( self.icons[x], '') 
                combo.setMinimumSize(self.iconSize[0],self.iconSize[1])
                combo.setMaximumSize(self.iconSize[0],self.iconSize[1])
                combo.setIconSize(QtCore.QSize(self.iconSize[0],self.iconSize[1]))
                callback = make_callback(self.env, name, vals)
                QtCore.QObject.connect(combo,QtCore.SIGNAL("activated(int)"), callback)
                self.layout.addWidget(combo)



    def show(self):
        QMainWindow.show(self)
        self.lsys.animate()



def main():
    app = QtGui.QApplication(sys.argv)

    style = '''QComboBox{
     margin: 0px;
     border: 0px;
     padding: 0px;
     }

     QPushButton{
     margin: 0px;
     border: 0px;
     padding: 0px;
     background-color: rgba(0,0,0,0); 
     }
'''
    app.setStyleSheet(style)

    lsys = Lsystem(get_shared_model('scienceFestivalNov09_ABC.lpy'))
    
    checkbox_values = {0:False, 1:True}
    gene_params = [(name, checkbox_values) for name in ['GA', 'GB', 'GC']]

    btn_imgs = ['B-DNA_'+str(x)+'m.png' for x in range(1,13)]
    btn_icons = [QtGui.QIcon(get_shared_image(fil)) for fil in btn_imgs]

    # Define all the combobox params
    curve_names,curves = zip(*lsys.context()['__curves__'])
    curve_values = dict(zip(range(len(curves)), curves))
    curve_params = [(name, curve_values) for name in curve_names]

    ang_params = [('phylangle',[x*20 for x in range(8)])]
    size_params = [('petal_length',range(4,12)), ('stamen_length',range(3,12)), ('carpel_length',range(3,12))]
    color_params = [('petal_color', range(8,16))]
    petal_curve_params = [ ('petal_nerve', [curve_values[k] for k in range(8,14)]) ]
    whorl_params = [('nb_petal', range(3,10))]

    params = petal_curve_params + color_params + size_params + whorl_params

    # Go
    window = Demo(lsys, params, btn_icons)
    window.show()
    app.exec_()
    

if __name__ == '__main__':
    main()