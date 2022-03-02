
# This file has been generated at $TIME

from openalea.core import *

def register_packages(pkgmanager):
    
    metainfo = {'description': 'growth demo using celltissue package', 'license': '', 'url': '', 'version': '1.0', 'authors': 'jerome Chopard', 'institutes': 'INRIA'} 
    pkg = UserPackage("CellTissue.growth", metainfo)

    

    nf = Factory( name="float scy",
                  description="Float Value",
                  category="Data Types,datatype",
                  nodemodule="local_nodes",
                  nodeclass="FloatScyNode",

                  inputs=(dict(name="str", interface=IStr, value="0.0"),),
                  outputs=(dict(name="Float", interface=IFloat),),
                  )

    pkg.add_factory( nf )


    nf = Factory(name='append', 
                 description='append a value to a list', 
                 category='Modelling', 
                 nodemodule='local_nodes',
                 nodeclass='AppendNode',
                 inputs=[{'interface': ISequence, 'name': 'list', 'value': []}, {'interface': None, 'name': 'val', 'value': None}],
                 outputs=[{'interface': ISequence, 'name': 'list'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='list', 
                 description='create a list from valid entries', 
                 category='Modelling', 
                 nodemodule='local_nodes',
                 nodeclass='ListNode',
                 inputs=[{'interface': None, 'name': 'val0', 'value': None, 'hide': False},
						 {'interface': None, 'name': 'val1', 'value': None, 'hide': True},
						 {'interface': None, 'name': 'val2', 'value': None, 'hide': True},
						 {'interface': None, 'name': 'val3', 'value': None, 'hide': True},
						 {'interface': None, 'name': 'val4', 'value': None, 'hide': True},
						 {'interface': None, 'name': 'val5', 'value': None, 'hide': True},
						 {'interface': None, 'name': 'val6', 'value': None, 'hide': True},
						 {'interface': None, 'name': 'val7', 'value': None, 'hide': True},
						 {'interface': None, 'name': 'val8', 'value': None, 'hide': True},
						 {'interface': None, 'name': 'val9', 'value': None, 'hide': True}],
                 outputs=[{'interface': ISequence, 'name': 'list'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='triangulation', 
                 description='triangulate a 2D tissue', 
                 category='Modelling', 
                 nodemodule='meris_algo',
                 nodeclass='WispTriangulationNode',
                 inputs=[{'interface': IInt, 'name': 'scale', 'value': 0}, {'interface': None, 'name': 'tissue', 'value': None}, {'interface': None, 'name': 'pos', 'value': None}],
                 outputs=[{'interface': None, 'name': 'triangulation'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='strain0', 
                 description='create strain for a triangulation', 
                 category='Modelling', 
                 nodemodule='meris_algo',
                 nodeclass='Strain0Node',
                 inputs=[{'interface': None, 'name': 'triangulation', 'value': None}],
                 outputs=[{'interface': None, 'name': 'strain'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='fixed cell', 
                 description='fixe a cell in space', 
                 category='Modelling', 
                 nodemodule='meris_algo',
                 nodeclass='FixedCellNode',
                 inputs=[{'interface': None, 'name': 'tissue', 'value': None},{'interface': IInt, 'name': 'cell', 'value': 0}],
                 outputs=[{'interface': ISequence, 'name': 'fixed'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='meca growth', 
                 description='container for mechanical parameters', 
                 category='Modelling', 
                 nodemodule='meris_algo',
                 nodeclass='MecaGrowthNode',
                 inputs=[{'interface': None, 'name': 'triangulation', 'value': None}, {'interface': None, 'name': 'thickness', 'value': None}, {'interface': IFloat, 'name': 'P', 'value': None}, {'interface': None, 'name': 'fixed', 'value': None}, {'interface': None, 'name': 'nu', 'value': None}, {'interface': None, 'name': 'E', 'value': None}, {'interface': None, 'name': 'G', 'value': None}, {'interface': IFloat, 'name': 'Gth', 'value': 0.2}, {'interface': None, 'name': 'strain0', 'value': None}],
                 outputs=[{'interface': None, 'name': 'algo'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='physiology', 
                 description='physiological reaction on one substance', 
                 category='Modelling', 
                 nodemodule='meris_process',
                 nodeclass='PhysiologyNode',
                 inputs=[{'interface': None, 'name': 'tissue', 'value': None}, {'interface': None, 'name': 'pos', 'value': None}, {'interface': None, 'name': 'D', 'value': None}, {'interface': None, 'name': 'decay', 'value': None}, {'interface': None, 'name': 'fixed', 'value': None}, {'interface': None, 'name': 'substance', 'value': None}],
                 outputs=[{'interface': None, 'name': 'process'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='growth', 
                 description='growth of a tissue', 
                 category='Modelling', 
                 nodemodule='meris_process',
                 nodeclass='GrowthNode',
                 inputs=[{'interface': None, 'name': 'pos', 'value': None}, {'interface': None, 'name': 'algo', 'value': None}, {'interface': ISequence, 'name': 'maps', 'value': []}],
                 outputs=[{'interface': None, 'name': 'process'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='division', 
                 description='cell division of a tissue', 
                 category='Modelling', 
                 nodemodule='meris_process',
                 nodeclass='CellDivisionNode',
                 inputs=[{'interface': None, 'name': 'tissue', 'value': None}, {'interface': None, 'name': 'pos', 'value': None}, {'interface': IFloat, 'name': 'Vref', 'value': 1.}, {'interface': ISequence, 'name': 'maps', 'value': []}],
                 outputs=[{'interface': None, 'name': 'process'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='cell state', 
                 description='change cell state', 
                 category='Modelling', 
                 nodemodule='meris_process',
                 nodeclass='CellStateNode',
                 inputs=[{'interface': None, 'name': 'driving map', 'value': None}, {'interface': None, 'name': 'map', 'value': None}, {'interface': IFloat, 'name': 'threshold', 'value': 0.}, {'interface': IFloat, 'name': 'mul', 'value': 1.}],
                 outputs=[{'interface': None, 'name': 'process'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='redraw', 
                 description='redraw some object view', 
                 category='Modelling', 
                 nodemodule='meris_display',
                 nodeclass='RedrawNode',
                 inputs=[{'interface': None, 'name': 'view', 'value': None}],
                 outputs=[{'interface': None, 'name': 'process'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='tissue view', 
                 description='create a meristem object', 
                 category='Modelling', 
                 nodemodule='meris_display',
                 nodeclass='MeristemView2DNode',
                 inputs=[{'interface': None, 'name': 'tissue', 'value': None}, {'interface': None, 'name': 'pos', 'value': None}, {'interface': None, 'name': 'morpho', 'value': None}, {'interface': None, 'name': 'physio', 'value': None}, {'interface': None, 'name': 'meca', 'value': None}],
                 outputs=[{'interface': None, 'name': 'view'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='loop', 
                 description='create a time loop', 
                 category='Modelling', 
                 nodemodule='meris_display',
                 nodeclass='LoopNode',
                 inputs=[{'interface': IFloat, 'name': 'dt', 'value': 1.0}, {'interface': IInt, 'name': 'nb steps', 'value': 100}],
                 outputs=[{'interface': ISequence, 'name': 'range'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )

    nf = Factory(name='simu', 
                 description='perform the simulation by modifying the meristem', 
                 category='Modelling', 
                 nodemodule='meris_display',
                 nodeclass='SimuLoopNode',
                 inputs=[{'interface': ISequence, 'name': 'processes', 'value': []}, {'interface': ISequence, 'name': 'times', 'value': []}],
                 outputs=[{'interface': None, 'name': 'loop'}],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )


    nf = Factory(name='simuGUI', 
                 description='GUI of simu node', 
                 category='Visualisation', 
                 nodemodule='meris_display',
                 nodeclass='SimuGUINode',
                 inputs=[{'interface': None, 'name': 'view', 'value': None}, {'interface': None, 'name': 'loop', 'value': None}],
                 outputs=[],
                 widgetmodule=None,
                 widgetclass=None,
                 )

    pkg.add_factory( nf )


    pkgmanager.add_package(pkg)


