# -*- coding: latin-1 -*-
from base import *



class AboutView(View):
    def __init__(self,parent = None):
        View.__init__(self,parent,'About')

        self.logos = ['1C1M', 'VP', 'CIRAD','Inria','INRA','Cambridge']
        self.buttongap = 20
        for i,logo in enumerate(self.logos):
            button = GLButton(parent, 20, 100*(i+1),  img = get_shared_image('Logo'+logo+'.png'))
            self.addButton(button)
        
        self.abouttxt = self.getTextFromFile()
        
        self.textbox = GLTextBox(parent, self.abouttxt, 300, 212, 800, 600)
        self.addWidget(self.textbox)
        
    def resizeWidgetEvent(self,w,h):
        toth = 0
        for button in self.buttons:
            toth += button.height
        toth += (len(self.buttons)-1)*self.buttongap
        starth = (h-toth)/2
        for button in self.buttons:
            button.move(button.x,starth)
            starth += button.height + self.buttongap
    
    def draw(self):
        pass