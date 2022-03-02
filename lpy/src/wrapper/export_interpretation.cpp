/* ---------------------------------------------------------------------------
 #
 #       L-Py: L-systems in Python
 #
 #       Copyright 2003-2008 UMR Cirad/Inria/Inra Dap - Virtual Plant Team
 #
 #       File author(s): F. Boudon (frederic.boudon@cirad.fr)
 #
 # ---------------------------------------------------------------------------
 #
 #                      GNU General Public Licence
 #
 #       This program is free software; you can redistribute it and/or
 #       modify it under the terms of the GNU General Public License as
 #       published by the Free Software Foundation; either version 2 of
 #       the License, or (at your option) any later version.
 #
 #       This program is distributed in the hope that it will be useful,
 #       but WITHOUT ANY WARRANTY; without even the implied warranty of
 #       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 #       GNU General Public License for more details.
 #
 #       You should have received a copy of the GNU General Public
 #       License along with this program; see the file COPYING. If not,
 #       write to the Free Software Foundation, Inc., 59
 #       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 #
 # ---------------------------------------------------------------------------
 */

#include "interpretation.h"
#include "axialtree.h"

#include <boost/python.hpp>
using namespace boost::python;
LPY_USING_NAMESPACE
PGL_USING_NAMESPACE

void export_Interpretation()
{
  def("helpTurtle",(std::string(*)())&LPY::helpTurtle);
  def("helpTurtle",(std::string(*)(const std::string&))&LPY::helpTurtle);
  def("turtle_interpretation",(void(*)(AxialTree&,Turtle&))&LPY::turtle_interpretation);
  def("turtle_interpretation",(void(*)(AxialTree&,Turtle&,const StringMatching&))&LPY::turtle_interpretation);
}
