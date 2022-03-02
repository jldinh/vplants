/* -*-c++-*- 
 *------------------------------------------------------------------------------
 *                                                                              
 *        openalea.container: utils package                                     
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

#include <boost/python.hpp>
using namespace boost::python;

void export_spring ();
void export_spring_fem ();
void export_mass_spring_solver ();
void export_chemistry_actor ();
void export_chemistry_solver ();
//void export_toto ();

BOOST_PYTHON_MODULE(_cphysics) {
	export_spring();
	export_spring_fem();
	export_mass_spring_solver ();
	export_chemistry_actor ();
	export_chemistry_solver ();
	//export_toto ();
}
