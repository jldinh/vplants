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

#include "cphysics/mechanics_utils.h"

namespace physics {
namespace mechanics {
	void copy_particules (const P2D_list& p1, P2D_list& p2) {
		for (P2D_list::const_iterator it = p1.begin();
		                              it != p1.end();
		                              ++it) {
			p2.push_back(Particule2D(*it) );
		}
	}
	
	void copy_particules (const P3D_list& p1, P3D_list& p2) {
		for (P3D_list::const_iterator it = p1.begin();
		                              it != p1.end();
		                              ++it) {
			p2.push_back(Particule3D(*it) );
		}
	}

};//mechanics
};//physics
