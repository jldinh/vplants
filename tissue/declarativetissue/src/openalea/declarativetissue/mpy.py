from kernel import *
from openalea.scheduler import *
from time import sleep

class MpyLoop (Loop):
    def __init__(self, rules = None) :
        Loop.__init__(self,Scheduler())
        self.rules = rules
    def _loop (self) :
        """Internal function that advance from one step.
        """
        if not self.rules.nbiterations is None:
            while self.rules.current_step < self.rules.nbiterations :
                if not self._running :
                    return
                self._step()
                sleep(0.01)
        else:
            while True:
                if not self._running :
                    return
                self._step()
                sleep(0.01)
    
    def _step (self) :
        """Perform one step of the scheduler
        in the current thread.
        """
        self.rules.step()
        self._current_step = self.rules.current_step
        self._post_step_processing()
        return self._current_step

def main():
  import sys
  if len(sys.argv) > 1:  
    from openalea.pglviewer import QApplication,Viewer,\
                                   ViewerGUI,TemplateGUI, LoopGUI, LoopView
    
    qapp = QApplication([])
    v = Viewer()
    
    print 'Process',sys.argv[1]
    kernel = RuleKernel(v,sys.argv[1])
    #kernel.run()
    kernel.init()
    v.view().bound_to_worlds()
    
    sc = kernel.namespace['sc']
    
    gui = TemplateGUI("tlpy")
    gui.add_action_descr("step",kernel.step)
    gui.add_action_descr("run",kernel.run)
    
    s = Scheduler()
    #s.register(Task(kernel.step,delay = 1,priority = 2,name='step'))
    l = MpyLoop(kernel)
    gui = LoopGUI(LoopView(l))
    
    v.add_gui(ViewerGUI(vars() ) )
    v.add_gui(gui)
    
    v.show()
    v.view().set_dimension(2)
    v.view().update()
    
    qapp.exec_()
  else:
    print 'help : mpy file.mpy'

if __name__ == '__main__':
    main()