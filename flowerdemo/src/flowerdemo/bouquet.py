from base import *
from config import *
from PyQt4.QtCore import QObject, SIGNAL

class BouquetView(LpyModelWithCacheView):
    def __init__(self,parent):
        LpyModelWithCacheView.__init__(self,parent,'Bouquet')
        self.animateMode = False
        
        self.cachefile = 'bouquet.txt'
        self.cacherep  = 'bouquet'
        
        self.actions = [ 'lfy', 'tfl1', 'geneA', 'lfyplus', 'tfl1plus']
        self.variables = [ 'lfymutant', 'tfl1mutant', 'ap1mutant', 'LFY35S', 'TFL135S']

        # first line of button
        self.button1width,self.button1heigth = 200,80
        self.buttongap = 10
        for action,var in zip(self.actions,self.variables):
            button = GLButton(parent, 100, 100, self.button1width, self.button1heigth, 
                                    img = get_shared_image(action+'.png'), 
                                    action = self.applyAction, togglable = True,params = [var])
            button.gene = True
            self.addButton(button)
            
        # second line of button
        self.button2width,self.button2heigth = 150,60
        for i in xrange(3,5):
            self.buttons[i].toggled = True
            self.buttons[i].resize(self.button2width,self.button2heigth)
        
        #variables
        self.variations = dict([(i,[True,False]) for i in self.variables])
        self.variables = dict([(i,False) for i in self.variables])
 
        self.buttonAnimate = GLButton(parent, 100, 100, 48, 48, 
                             img = get_shared_image('animate.png'), 
                             action = self.toggleAnimateMode, togglable = True)
        self.buttonAnimate.toggled = True
        self.addButton(self.buttonAnimate)
        
        QObject.connect(self,SIGNAL('animationStarted()'),parent.disableButtonInteraction)
        QObject.connect(self,SIGNAL('animationStopped()'),parent.enableButtonInteraction)
        
        self.createHelpWidgetFromFile()
        
        self.setLsystem('bouquet_arabido.lpy')
    def init(self):
        LpyModelWithCacheView.init(self)
        self.animateMode = False
        
    def openView(self):    
        LpyModelWithCacheView.openView(self)
        
        self.animateMode = False
        
        # init buttons
        self.resizeWidgetEvent(self.widget.width(),self.widget.height())
        
        # init view
        self.setView()
        
        # show model
        self.run()

    def resizeWidgetEvent(self,w,h):
        LpyModelWithCacheView.resizeWidgetEvent(self,w,h)
        
        startw = (w - (3 * self.button1width + 2 * self.buttongap))/2.0
        starth = h-20- self.button1heigth-self.button2heigth-self.buttongap
        
        for i in xrange(3):
            button = self.buttons[i]
            button.move(startw,starth)
            startw += self.button1width+self.buttongap
        
        startw = (w - (2 * self.button2width + self.buttongap))/2.0
        starth = h - 20- self.button2heigth
        for i in xrange(3,5):
            button = self.buttons[i]
            button.move(startw,starth)
            startw += self.button2width+self.buttongap

        self.buttonAnimate.move(w-self.buttonAnimate.width-20,70)
    
    def setView(self):
        camera = self.widget.camera()
        center = Vec(0,0,0)
        camera.setRevolveAroundPoint(center)
        
        camera.setPosition(Vec(52,-11.2,45))
        camera.setViewDirection(Vec(-0.879266,0.192891,-0.435528))
        camera.setUpVector(Vec(-0.428212,0.080382,0.900096))
        #camera.lookAt(Vec(0,0,20))
        camera.setSceneRadius(70)

    def applyAction(self,organ):
        self.variables[organ] = not self.variables[organ]
        self.viewModel()
        
    def viewModel(self):
        if not self.animateMode:
            self.run()
        else:
            self.animate()

    def toggleAnimateMode(self):
        if self.animateMode:
            if self.lsystem.isRunning():
                self.lsystem.early_return = True
        self.animateMode = not self.animateMode        
        self.viewModel()
