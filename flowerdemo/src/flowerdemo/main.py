
def oldmain():
    from cambridgedemo import main
    main()

from PyQt4.Qt import QApplication,QMainWindow
from base import DemoWidget, SceneView
from starter import MenuView
from naked import NakedView
from abcmodel import ABCView
from bouquet import BouquetView
from geneshape import GeneShapeView
from about import AboutView

def help():
    print 'FlowerDemo'
    print ' --help -h : This help'
    print ' --no-fullscreen : Do not use fullscreen mode'
    print ' --no-cache : Do not use cache to speedup start of this application'
    print ' --re-cache : Recompute cache'
    

def main(args = None):
    if args is None:
        import sys
        args = sys.argv
        
        
    if '-h' in args or '--help' in args: 
        help()
        return
    
    
    app = QApplication(args)
    
    mainwindow = QMainWindow()
    window = DemoWidget()
    mainwindow.setCentralWidget(window)
    panels = []
    pid = window.appendView(NakedView(window))
    panels += [(pid,'deshabillezmoi.png')]
    pid = window.appendView(GeneShapeView(window))
    panels += [(pid,'formegene.png')]
    pid = window.appendView(ABCView(window))
    panels += [(pid,'abc.png')]
    if '-3' not in args:
        pid = window.appendView(BouquetView(window))
        panels += [(pid,'bouquet.png')]
    #pid = window.appendView(SceneView(window))
    #panels += [(pid,'fleuralautre.png')]
    menu = MenuView(window)
    menuid = window.appendInitialView(menu)
    menu.setPanels(panels)
    window.appendAboutView(AboutView(window))
    #window.setCurrentViewId(1)
    print 'show'
    if '--no-fullscreen' in args:
        mainwindow.resize(800,600)
        mainwindow.show()
    else:
        mainwindow.showFullScreen()   
    app.exec_()
    
    
if __name__ == '__main__':
    import sys
    main(sys.argv)