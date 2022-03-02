/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: The Plant Graphic Library
 *
 *       Copyright 1995-2007 UMR CIRAD/INRIA/INRA DAP 
 *
 *       File author(s): F. Boudon et al.
 *
 *  ----------------------------------------------------------------------------
 *
 *                      GNU General Public Licence
 *
 *       This program is free software; you can redistribute it and/or
 *       modify it under the terms of the GNU General Public License as
 *       published by the Free Software Foundation; either version 2 of
 *       the License, or (at your option) any later version.
 *
 *       This program is distributed in the hope that it will be useful,
 *       but WITHOUT ANY WARRANTY; without even the implied warranty of
 *       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 *       GNU General Public License for more details.
 *
 *       You should have received a copy of the GNU General Public
 *       License along with this program; see the file COPYING. If not,
 *       write to the Free Software Foundation, Inc., 59
 *       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 *  ----------------------------------------------------------------------------
 */

#include "export_printer.h"
#include <plantgl/algo/codec/pyprinter.h>
#include <boost/python.hpp>

/* ----------------------------------------------------------------------- */

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace boost::python;

/* ----------------------------------------------------------------------- */

class PyStrPyPrinter : public PyStrPrinter, public PyPrinter { 
public:
	PyStrPyPrinter() :  PyPrinter(_mystream) {}     
};

class PyFilePyPrinter : public PyFilePrinter, public PyPrinter { 
public:
	PyFilePyPrinter(const std::string& fname) : PyFilePrinter(fname), PyPrinter(_mystream) {}   
};  

/* ----------------------------------------------------------------------- */

// std::string get

void export_PyPrinter()
{
 class_< PyPrinter, bases< Printer >, boost::noncopyable > ( "PyPrinter" , no_init )
	.add_property("indentation", make_function(&PyPrinter::getIndentation,return_value_policy<return_by_value>()), &PyPrinter::setIndentation )
	.add_property("indentation_increment", make_function(&PyPrinter::getIndentationIncrement,return_value_policy<return_by_value>()), &PyPrinter::setIndentationIncrement )
	.add_property("pglnamespace", make_function(&PyPrinter::getPglNamespace,return_value_policy<return_by_value>()), &PyPrinter::setPglNamespace )
	.add_property("reference_dir", make_function(&PyPrinter::getReferenceDir,return_value_policy<return_by_value>()), &PyPrinter::setReferenceDir )
	.add_property("line_between_object", make_function(&PyPrinter::getLineBetweenObject,return_value_policy<return_by_value>()), &PyPrinter::setLineBetweenObject )
    .def("incrementIndentation",&PyPrinter::incrementIndentation)
    .def("decrementIndentation",&PyPrinter::decrementIndentation)

    ;

  class_< PyStrPyPrinter , bases< PyStrPrinter, PyPrinter > , boost::noncopyable> 
	  ("PyStrPrinter",init<>("String Printer in python format" ))
	  .def(str_printer_clear<>());
	  ;

  class_< PyFilePyPrinter , bases< PyFilePrinter, PyPrinter > , boost::noncopyable> 
	  ("PyFilePrinter",init<const std::string&>("File Printer in python format",args("filename")) );
    ;
}

/* ----------------------------------------------------------------------- */
