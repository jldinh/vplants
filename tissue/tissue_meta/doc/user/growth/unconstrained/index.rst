.. _tissue_growth_unconstrained:

########################################
Unconstrained Growth
########################################

:Version: |version|
:Release: |release|
:Date: |today|

The goal of this document is to describe a simple simulation in which a filamentous organism grow and divide in a nutrient field. The python script for this example can be downloaded (download file: :download:`simu.py`) and run in a shell console using::

	user@computer:$ python simu.py


.. warning:: This simulation grow cell by insertion. This is opposite to tip growth more usually encountered in plants.

-------------------------
Nutrient field
-------------------------

Creation
###################

The nutrient field is represented as a grid with nutrients stored in each box of the grid. The size of the grid (GS) must be sufficient to allow the development of a colony inside whereas the size of each box (BS) must be sufficiently small to establish gradients of nutrient.

.. literalinclude:: simu.py
    :start-after: #begin nutrient field create
    :end-before: #end nutrient field create

Interaction
###################

We define two antagonist functions to interact with the nutrient field. The first one increase the level of nutrients around a given point whereas the second deplete the level of nutrients around it.

.. literalinclude:: simu.py
    :start-after: #begin nutrient field interact
    :end-before: #end nutrient field interact

-------------------------
Organism
-------------------------

Creation
##################

This simulation model a filamentous organism like a colony of bacteria harvesting food in a liquid environment. The topology of the colony is described using a mesh of degree 1 where edges stands for cells and points mark the connection between two neighbor cells. The simulation starts with a colony formed by a single cell attached on one side.

.. literalinclude:: simu.py
    :start-after: #begin colony create
    :end-before: #end colony create

Nutrient Uptake
##################

Each cell of the colony will feed with the nutrients that are in it's vicinity. Basically, a cell will absorb and store a fraction of the nutrients in each box it cross.

.. literalinclude:: simu.py
    :start-after: #begin colony uptake
    :end-before: #end colony uptake

Cell Growth
##################

The growth of each cell depend on the level of nutrients they store. Since the colony float in a waterlike medium, there is no constraint on the growth. A cell in the middle of the colony can grow, gently pushing it's neighbors.

.. literalinclude:: simu.py
    :start-after: #begin colony growth
    :end-before: #end colony growth

Cell Division
##################

As soon as a cell is too big, it divides, creating 5 daughters cells:
 - 3 of them, replacing the old one
 - 2 of them branching on the side to simulate foraging

.. literalinclude:: simu.py
    :start-after: #begin colony divide
    :end-before: #end colony divide

--------------------------------
Display
--------------------------------

Each cell of the colony is displayed as a segment whose color depends on the level of nutrient stored in the cell.

.. literalinclude:: simu.py
    :start-after: #begin colony display
    :end-before: #end colony display

The nutrient field is displayed too. A sphere whose size depends on the amount of nutrient in a box is displayed in the center of each box.

.. literalinclude:: simu.py
    :start-after: #begin nutrient field display
    :end-before: #end nutrient field display


.. warning:: If the simulation is too slow, it might be due to the redraw of the nutrient field (huge number of spheres). Try to desactivate it if needed.

--------------------------------
Scheduler
--------------------------------

In order to organize and iterate through the different tasks, a scheduler is defined.

.. literalinclude:: simu.py
    :start-after: #begin create scheduler
    :end-before: #end create scheduler


--------------------------------
Launch Simulation
--------------------------------

The only left is to define a GUI to interact with the scheduler and display the tissue. The user can locally increase or descrease the level of nutrients.

.. literalinclude:: simu.py
    :start-after: #begin defines gui
    :end-before: #end defines gui

Everything is assembled and displayed.

.. literalinclude:: simu.py
    :start-after: #begin launch simu
    :end-before: #end launch simu

.. table:: Simulation results

    +-----------------------------------+-----------------------------------+-----------------------------------+
    |  .. image:: res_step0.png         |.. image:: res_step1.png           |  .. image:: res_step2.png         |
    |      :width: 100%                 |    :width: 100%                   |      :width: 100%                 |
    |      :align: center               |    :align: center                 |      :align: center               |
    +-----------------------------------+-----------------------------------+-----------------------------------+


