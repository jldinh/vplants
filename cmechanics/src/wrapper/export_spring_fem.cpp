/* -*-c++-*- 
 *------------------------------------------------------------------------------
 *                                                                              
 *        openalea.cmechanics: wrapper package                                  
 *                                                                              
 *        Copyright 2006 INRIA - CIRAD - INRA                      
 *                                                                              
 *        File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>         
 *                                                                              
 *        Distributed under the Cecill-C License.                               
 *        See accompanying file LICENSE.txt or copy at                          
 *            http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html       
 *                                                                              
 *        OpenAlea WebSite : http://openalea.gforge.inria.fr                    
 *       
 *                                                                       
 *-----------------------------------------------------------------------------*/

#include "cmechanics/spring_fem.h"

using namespace mechanics;

#include <boost/python.hpp>
#include <boost/python/tuple.hpp>
using namespace boost::python;

void set_python_material (TriangleMembrane3D& tr, const tuple& m) {
	Tensor2222 mat;
	int ind = 0;
	for (int i = 0; i < 2; ++i) {
		for (int j = 0; j < 2; ++j) {
			for (int k = 0; k < 2; ++k) {
				for (int l = 0; l < 2; ++l) {
					mat(i,j,k,l) = extract<double>(m[ind]);
					ind += 1;
				}
			}
		}
	}
	
	tr.set_material(mat);
}

void export_spring_fem () {
	class_<TriangleMembrane3D, bases<Spring3D> >("CTriangleMembrane3D",init<int,int,int,double,double,double,double>())
		.def("set_material",&set_python_material,"set a material defined in python")
		;
}
