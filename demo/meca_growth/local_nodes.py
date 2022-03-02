from os.path import dirname
from openalea.core import Node

class LocalNode(object):
    def __call__(self, *inputs):
        rep=dirname(__file__)
        return (rep,)

class FloatScyNode(Node):
    """
Variable
Input 0 : The stored value in string format
Ouput 0 : Transmit the stored value
    """

    def __init__(self, ins, outs):
        Node.__init__(self, ins, outs)
        self.set_caption(str(0.0))
       

    def __call__(self, inputs):
        """ inputs is the list of input values """
        res = float(inputs[0])
        self.set_caption('%.1e'%res)
        return ( res, )

class AppendNode(object):
    def __call__(self, *inputs) :
        l,val=inputs
        return (list(l+[val]),)

class ListNode(object):
    def __call__(self, *inputs) :
        return ([v for v in inputs if v is not None],)


