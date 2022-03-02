from openalea.core.alea import *

pm = PackageManager()
pm.init(verbose=False)


reconstruction_names = ['fusion_v1',
                        'mars',
                        'positioning_landmarks',
                        'registration:auto_linear',
                        'registration:auto_non_linear',
                        'registration:landmarks',
                        'tasks:fusion',
                        'tasks:reconstruction',
                        'tasks:reconstruction_with_init']

segmentation_demos = ['filtering',
                      'full_segmentation',
                      'seed_extraction',
                      'watershed',
                      'over_segmentation']

analysis_demos = ['analysis',
                  'extract_L1']

structural_analysis_demos = ['draw_walls',
                             'draw_L1']


from PyQt4 import QtGui
app = QtGui.QApplication([])

def test_reconstruction_demos():
    for i in range(0, len(reconstruction_names)):
        yield check,'reconstruction', reconstruction_names[i]

def test_segmentation_demos():
    for i in range(0, len(segmentation_demos)):
        yield check,'segmentation', segmentation_demos[i]

def test_analysis_demos():
    for i in range(0, len(analysis_demos)):
        yield check,'analysis', analysis_demos[i]

def test_structural_analysis_demos():
    for i in range(0, len(structural_analysis_demos)):
        yield check,'structural_analysis', structural_analysis_demos[i]

def check(wralea, name):
    res = run(('vplants.mars_alt.demo.%s' % wralea, name),{},pm=pm)

