from openalea.lpy import *

def test_kwd():
   ''' test matching with **kwd '''
   for optionvalue in [1,2]:
       l = Lsystem('test_kwd.lpy')
       l.context().options.setSelection('Module matching',optionvalue)
       l.iterate()

def test_kwd2():
   ''' test matching with **kwd '''
   for optionvalue in [1,2]:
       l = Lsystem('test_kwd2.lpy')
       l.context().options.setSelection('Module matching',optionvalue)
       l.iterate()
