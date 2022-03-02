/* -*-c++-*- 
 *------------------------------------------------------------------------------
 *                                                                              
 *        openalea.cmechanics: mechanics utils package                          
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

#include "cmechanics/mechanics_utils.h"

namespace mechanics {
	void copy_particules (const P2D_list& p1, P2D_list& p2) {
		P2D_list::const_iterator it1 = p1.begin();
		P2D_list::iterator it2 = p2.begin();
		for (;it1 != p1.end();++it1) {
			it2->copy(*it1);
			++it2;
		}
	}
	
	void copy_particules (const P3D_list& p1, P3D_list& p2) {
		P3D_list::const_iterator it1 = p1.begin();
		P3D_list::iterator it2 = p2.begin();
		for (;it1 != p1.end();++it1) {
			it2->copy(*it1);
			++it2;
		}
	}
	
	void copy_positions (const P2D_list& p1, P2D_list& p2) {
		P2D_list::const_iterator it1 = p1.begin();
		P2D_list::iterator it2 = p2.begin();
		for (;it1 != p1.end();++it1) {
			it2->copy_position(*it1);
			++it2;
		}
	}
	
	void copy_positions (const P3D_list& p1, P3D_list& p2) {
		P3D_list::const_iterator it1 = p1.begin();
		P3D_list::iterator it2 = p2.begin();
		for (;it1 != p1.end();++it1) {
			it2->copy_position(*it1);
			++it2;
		}
	}

};//mechanics
