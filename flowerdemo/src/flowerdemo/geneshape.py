from base import *
from PyQt4 import QtGui, QtCore
from config import *

def roundup(a,b):
    m,r = divmod(a,b)
    return m + (1 if r > 0 else 0)

class GeneShapeView(LpyModelView):
    def __init__(self,parent):
        LpyModelView.__init__(self,parent,'FormeDesGenes')
        self.setLsystem('scienceFestivalNov09_ABC.lpy')
        
        self.iconSize = (200,80)
        self.imgs = ['B-DNA_'+str(x)+'m.png' for x in range(1,13)]
        self.icons = [QtGui.QIcon(get_shared_image(fil)) for fil in self.imgs]
        
        curve_names,curves = zip(*self.lsystem.context()['__curves__'])
        curve_values = dict(zip(range(len(curves)), curves))
        
        petal_curve_parameter = [ ('petal_nerve', [curve_values[k] for k in range(8,14)]) ]
        color_parameter = [('petal_color', range(8,16))]
        
        petal_length_parameter = [('petal_length',range(4,12)) ]
        stamen_length_parameter = [('stamen_length',range(3,12))] 
        carpel_length_parameter = [('carpel_length',range(3,12)) ]
        
        whorl_parameter = [('nb_petal', range(3,10))]
        
        self.variations = petal_curve_parameter + color_parameter 
        self.variations += petal_length_parameter + stamen_length_parameter + carpel_length_parameter 
        self.variations += whorl_parameter
        self.nbparameters = len(self.variations)

        self.targetwidth = QApplication.desktop().screenGeometry().width()
        maxIconWidth = (self.targetwidth - ((self.nbparameters +1) * 10 ))/ self.nbparameters
        iconratio = float(maxIconWidth) / self.iconSize[0]
        self.iconSize = (maxIconWidth,self.iconSize[1]*iconratio)
        
        self.maxgenebyline = self.nbparameters
        self.nblines = 1
        self.genebyline = self.maxgenebyline
        
        # self.maxgenebyline = self.targetwidth / self.iconSize[0]
        # self.nblines = roundup(self.nbparameters, self.maxgenebyline)
        # self.genebyline = roundup(self.nbparameters,self.nblines)

        self.createHelpWidgetFromFile('formegene.txt')
     
    def initLayout(self):
        self.vlayout = QtGui.QVBoxLayout(self.widget)
        self.vlayout.addStretch(0)
        self.hlayout1 = QtGui.QHBoxLayout()
        self.vlayout.addLayout(self.hlayout1)
        self.hlayout2 = QtGui.QHBoxLayout()
        self.vlayout.addLayout(self.hlayout2)

        def make_callback( n, d):
            def anon(value):
                self.variables[n] = d[value]
                self.run()
            return anon
        
        i = 0
        self.combos = []
        layout = self.hlayout1
        layout.addStretch(0)
        for name, values in self.variations:
                # combobox
                combo = QtGui.QComboBox()
                self.combos.append(combo)
                for x in range(len(values)):
                    combo.addItem( self.icons[x], '') 
                combo.setMinimumSize(self.iconSize[0],self.iconSize[1])
                combo.setMaximumSize(self.iconSize[0],self.iconSize[1])
                combo.setIconSize(QtCore.QSize(self.iconSize[0],self.iconSize[1]))
                callback = make_callback(name, values)
                QtCore.QObject.connect(combo,QtCore.SIGNAL("activated(int)"), callback)
                combo.hide()
                
                if i == self.genebyline : 
                    layout.addStretch(0)
                    layout = self.hlayout2
                    layout.addStretch(0)
                layout.addWidget(combo)
                
                i += 1
        layout.addStretch(0)

        
    def initView(self):
        LpyModelView.initView(self)
        self.initLayout()
        
    def openView(self):
        LpyModelView.openView(self)
        
        for combo in self.combos:
            combo.show()
        self.widget.setLayout(self.vlayout)
        
        # init buttons
        # self.resizeWidgetEvent(self.widget.width(),self.widget.height())
        
        # init view
        self.setView()
        
        # show model
        self.run()
        
    def closeView(self):
        LpyModelView.closeView(self)
        for combo in self.combos:
            combo.hide()
        

    def setView(self):
        camera = self.widget.camera()
        center = Vec(0,0,0)
        camera.setRevolveAroundPoint(center)
         
        camera.setPosition(Vec(2.5,-0.32,2.84))
        camera.setViewDirection(Vec(-0.71,0.05,-0.69))
        camera.setUpVector(Vec(-0.69,0,0.71))
        camera.setSceneRadius(3)
            

    