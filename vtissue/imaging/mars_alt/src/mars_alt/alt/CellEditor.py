#-*- python -*-
# -*- coding: latin-1 -*-
#
#       mars_alt.alt.CellEditor
#
#       Copyright 2006 - 2011 INRIA - CIRAD - INRA
#
#       File author(s): Eric MOSCARDI <eric.moscardi@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################
"""
Implementation of a TableEditor

This class is used for display the mapping.
"""

__license__= "Cecill-C"
__revision__ = " $Id$ "

# Import statements:
try:
    from enthought.traits.api import (HasTraits, HasStrictTraits, 
                                  Str, Int, List, Button)
except:
    from traits.api import (HasTraits, HasStrictTraits, 
                                  Str, Int, List, Button)


try:
    from enthought.traits.ui.api import View, Group, Item, TableEditor
except:
    from traitsui.api import View, Group, Item, TableEditor

try:
    from enthought.traits.ui.table_column import ObjectColumn, ExpressionColumn
except:
    from traitsui.table_column import ObjectColumn, ExpressionColumn
try:
    from enthought.traits.ui.table_filter import (EvalFilterTemplate, 
                                              MenuFilterTemplate, 
                                              RuleFilterTemplate, 
                                              EvalTableFilter)
except:
    from traitsui.table_filter import (EvalFilterTemplate, 
                                              MenuFilterTemplate, 
                                              RuleFilterTemplate, 
                                              EvalTableFilter)

# A helper class for the 'Department' class below:



class Cells ( HasTraits ):
    """Class of potential cell lineages. 'daughters' is a List of cells possibly descended from the cell 'mother'.
    """
    mother = Int
    daughters  = List(Int)
 

    traits_view = View(
        'mother', 'daughters',
        title   = 'Mapping',
        width   = 0.18,
        #buttons = [ 'OK', 'Cancel' ]
    )


# The definition of the demo TableEditor:
table_editor = TableEditor(
    columns = [ ObjectColumn( name = 'mother', width = 0.20, editable = False, horizontal_alignment = 'center' ),
                ObjectColumn( name = 'daughters',  width = 0.20, editable = False, horizontal_alignment = 'center' ) ],
    deletable   = True,
    sort_model  = True,
    #show_toolbar = True,
    auto_size   = False,
    auto_add     = True,
    orientation = 'vertical',
    edit_view   = View(
                      Group( 'mother', 'daughters',
                             show_border = True
                      ),
                      resizable = True
                  ),
    #filters     = [ EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate ],
    #search      = EvalTableFilter(),
    row_factory = Cells )

# The class to be edited with the TableEditor:
class Mapping ( HasStrictTraits ):
    """Objects containing a list of potential lineages.
    """
    #~ /add = Button('Add Lineage')
    #~ link = Button('Link')

    cells = List( Cells )
    save=Button(label="save current lineage")

    traits_view = View(
        Item("save"),
        Group(
            Item( 'cells',
                  show_label  = False,
                  editor      = table_editor
            ),
            #Item( 'add',
            #       show_label   = False
            #),
            show_border = True,
        ),
        title     = 'Mapping',
        width     = .4,
        height    = .4,
        resizable = True,
        kind      = 'live'
    )
    
    def _save_fired(self):
        print "save fired", [i.mother for i in self.cells]
        try:
            f=open("current_lineage.txt","w")
        except IOError:
            print "saving lineage impossible"
            return
        for i in self.cells:
            f.write(str(i.mother))
            f.write(" ")
            for d in i.daughters:
                f.write(str(d))
                f.write(" ")
            f.write("\n")
        f.close()

    def _add_changed ( self ):
        """Adds lineage to list of potential lineages 'cells'.
        """
        self.cells.append( Cells() )




# Create some cells:
#~ cells = [Cells()]

# Create the demo:
#~ demo = Mapping( cells = cells )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
