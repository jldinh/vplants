from base import *
from config import *

class ABCView(LpyModelView):
    def __init__(self,parent):
        LpyModelView.__init__(self,parent,'ABC')
        self.setLsystem('arabido-abc.lpy')
       
        self.buttonwidth,self.buttonheigth = 200,80
        self.buttongap = 10

        self.actions = [ 'A', 'B', 'C']
        self.variables  = dict([ ('G'+i,True) for i in self.actions ]+[('REPONSE',False),('stemflag',False)])
        
        self.actionbuttons = []
        for action in self.actions:
            button = GLButton(parent, 100, 100, self.buttonwidth, self.buttonheigth, 
                                    img = get_shared_image('gene'+action+'.png'), 
                                    action = self.applyAction, togglable = True,params = ['G'+action])
            self.addButton(button)
            self.actionbuttons.append(button)
        
        self.buttonVisualHelp = GLButton(parent, 100, 100, 48, 48, 
                          img = get_shared_image('book.png'), 
                          action = self.applyAction, togglable = True,params = ['REPONSE'])
                          
        self.buttonVisualHelp.gene = False
        self.buttonVisualHelp.toggled = True
        self.addButton(self.buttonVisualHelp)

        self.createHelpWidgetFromFile('abc.txt')
            
    def openView(self):
        LpyModelView.openView(self)
        
        # init buttons
        self.resizeWidgetEvent(self.widget.width(),self.widget.height())
        
        # init view
        self.setView()
        
        # show model
        self.run()

    def resizeWidgetEvent(self,w,h):
        LpyModelView.resizeWidgetEvent(self,w,h)
        
        startw = (w - (len(self.actions) * self.buttonwidth + (len(self.actions)-1) * self.buttongap))/2.0
        starth = h-20-self.buttonheigth
        for button in self.actionbuttons:
            button.move(startw,starth)
            startw += self.buttonwidth+self.buttongap

        self.buttonVisualHelp.move(w-self.buttonVisualHelp.width-20,70)
    
    def setView(self):
        camera = self.widget.camera()
        center = Vec(0,0,0)
        camera.setRevolveAroundPoint(center)
         
        camera.setPosition(Vec(1.8,-0.12,3.35))
        camera.setUpVector(Vec(0,0,1))
        camera.setViewDirection(Vec(-0.63,0.05,-0.8))
        camera.setSceneRadius(3)
            
            
    def applyAction(self,organ):
        self.variables[organ] = not self.variables[organ]
        self.run()
        
    def showHelp(self):
        pass
    