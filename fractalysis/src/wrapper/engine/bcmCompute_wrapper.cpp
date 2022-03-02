/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       Copyright 2005-2008 UMR DAP 
 *
 *       File author(s): D. Da SILVA (david.da_silva@cirad.fr)
 *                       F. BOUDON (frederic.boudon@cirad.fr)
 *
 *       $Id: gridcomputer.cpp,v 1.4 2006/06/20 10:22:57 fboudon Exp $
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

#include <boost/python.hpp>
#include "fractalysis/engine/bcmCompute.h"

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace boost::python;
using namespace std;

typedef vector<pair<Vector3,float> > FrPointList;
typedef vector<pair<int,double> > FrResult; //vecteur de couple pour transformer en liste ?

boost::python::object FrPList_to_list(FrPointList * fpl)
{
  boost::python::list points;
  for(size_t i=0; i<fpl->size(); ++i)
  {
    points.append(make_tuple(make_tuple((*fpl)[i].first.x(),(*fpl)[i].first.y(),(*fpl)[i].first.z()), (*fpl)[i].second));
  }
  return points;
}

boost::python::object pyPointDiscretize(const ScenePtr& scene)
{
    if (!scene || scene->isEmpty() ) return boost::python::object();
    return FrPList_to_list(pointDiscretize(scene));
}

boost::python::object pyComputeGrid(const ScenePtr& scene, int gridSize)
{
	if (!scene || scene->isEmpty() || gridSize < 2) return boost::python::object();
	pair<int,double> cres =  computeGrid(scene, gridSize);
	return make_tuple(cres.first,cres.second);
}

boost::python::object pyComputeGrids(const ScenePtr& scene, int maxGridSize)
{
	if (!scene || scene->isEmpty() || maxGridSize < 2) return boost::python::object();
	FrResult cres =  computeGrids(scene, maxGridSize);
	boost::python::list pyres;
	for(FrResult::const_iterator itRes = cres.begin(); itRes != cres.end(); ++itRes)
	{
		pyres.append(make_tuple(itRes->first,itRes->second));
	}
	return pyres;
}


void module_bcmcompute()
{
	def("pointDiscretize"  ,&pyPointDiscretize, args("scene"));
	def("computeGrid"  ,&pyComputeGrid, args("scene","gridSize"));
	def("computeGrids" ,&pyComputeGrids, args("scene","maxGridSize"));
}


BOOST_PYTHON_MODULE(_bcmcompute)
{
	module_bcmcompute();
}
