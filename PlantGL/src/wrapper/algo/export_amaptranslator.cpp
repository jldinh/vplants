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
  
#include <plantgl/scenegraph/geometry/amapsymbol.h>
#include <plantgl/algo/base/amaptranslator.h>
#include <plantgl/algo/base/discretizer.h>

#include <boost/python.hpp>
#include <boost/python/make_constructor.hpp>

/* ----------------------------------------------------------------------- */

PGL_USING_NAMESPACE
using namespace boost::python;

/* ----------------------------------------------------------------------- */

void export_AmapTranslator()
{
  class_< AmapTranslator,bases< Action >,boost::noncopyable >
    ( "AmapTranslator", init<Discretizer&>("AmapTranslator(Discretizer d) -> Translate a Geom object to an Amap Symbol."))
    .def("setNormalized",&AmapTranslator::setNormalized)
    .def("isNormalized",&AmapTranslator::isNormalized)
	.add_property("symbol",&AmapTranslator::getSymbol)
	.add_property("result",&AmapTranslator::getSymbol)
    ;
}

/* ----------------------------------------------------------------------- */
