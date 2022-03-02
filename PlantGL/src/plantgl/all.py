from math import *
from scenegraph import *
from algo import *
try:
    from gui import *
except:
    from gui3 import *
import codec


from os.path import join as pj

def get_shared_data(file, share_path=pj('share','plantgl', 'database')):
    from openalea.deploy.shared_data import get_shared_data_path
    import openalea.plantgl
    shared_data_path = get_shared_data_path(openalea.plantgl.__path__, share_path=share_path)
    return pj(shared_data_path, file)


