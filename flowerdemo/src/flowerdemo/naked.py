from base import *
from config import *

class NakedView(LpyModelView):
    def __init__(self,parent):
        LpyModelView.__init__(self,parent,'DeshabillezMoi')
        self.setLsystem('virtual-flower-Palais_2.2-arabido.lpy')
        self.bbx = BoundingBox(self.lsystem.sceneInterpretation(self.lsystem.iterate()))
        
        self.buttonwidth,self.buttonheigth = 150/2.,170/2.
        self.buttongap = 10

        self.actions = [ 'stem', 'sepal', 'petal','stamen', 'carpel']
        self.variables  = dict([ (i+'flag',True) for i in self.actions ])
        
        self.actionbuttons = []
        for action in self.actions:
            button = GLButton(parent, 100, 100, self.buttonwidth, self.buttonheigth, 
                                    img = get_shared_image(action+'.png'), 
                                    action = self.applyAction, togglable = True,params = [action+'flag'])
            button.name = action
            self.actionbuttons.append(button)
            self.addButton(button)
        
        self.createHelpWidgetFromFile('deshabillezmoi.txt')
        
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
        
    def setView(self):
        camera = self.widget.camera()
        if self.variables['stemflag'] :
            center = Vec(0.161041,0.00831789,2.53128)
            camera.setRevolveAroundPoint(center)
            
            camera.setPosition(Vec(4.74832,4.66647,8.79487))
            camera.setUpVector(Vec(0,0,1))
            camera.lookAt(center)
            camera.setSceneRadius(7)
            
        else:
            center = Vec(0,0,0)
            camera.setRevolveAroundPoint(center)
            camera.setPosition(Vec(2.3,0,2.8))
            camera.setUpVector(Vec(-0.637331,0.0113828,0.770506))
            camera.setViewDirection(Vec(-0.770435,0.0106725,-0.63743))
            camera.setSceneRadius(3)
            
            
    def applyAction(self,action):
        self.variables[action] = not self.variables[action]
        if action == 'stemflag':  
            self.setView()
        self.run()
            