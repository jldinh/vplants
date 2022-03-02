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

#include <boost/python.hpp>
using namespace boost::python;

void export_spring ();
void export_spring_fem ();
void export_mass_spring_solver ();

BOOST_PYTHON_MODULE(_cmechanics) {
	export_spring();
	export_spring_fem();
	export_mass_spring_solver ();
}
