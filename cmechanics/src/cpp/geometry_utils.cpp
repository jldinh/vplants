/* -*-c++-*- 
 *------------------------------------------------------------------------------
 *                                                                              
 *        openalea.cmechanics: geometry utils package                           
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

#include "cmechanics/geometry_utils.h"

namespace mechanics {
	/* *******************************************************
	*
	*	Tensor22
	*
	*********************************************************/
	Tensor22::Tensor22 () {
		for (int i = 0; i < 2; ++i) {
			_coeff.push_back(vector<double> (2) );
			for (int j = 0; j < 2; ++j) {
				_coeff[i].push_back(0.);
			}
		}
	}

	/* *******************************************************
	*
	*	Tensor32
	*
	*********************************************************/
	Tensor32::Tensor32 () {
		for (int i = 0; i < 3; ++i) {
			_coeff.push_back(vector<double> (2) );
			for (int j = 0; j < 2; ++j) {
				_coeff[i].push_back(0.);
			}
		}
	}

	/* *******************************************************
	*
	*	Tensor2222
	*
	*********************************************************/
	Tensor2222::Tensor2222 () {
		for (int i = 0; i < 2; ++i) {
			_coeff.push_back(vector<vector<vector<double> > > (2) );
			for (int j = 0; j < 2; ++j) {
				_coeff[i].push_back(vector<vector<double> > (2) );
				for (int k = 0; k < 2; ++k) {
					_coeff[i][j].push_back(vector<double> (2) );
					for (int l = 0; l < 2; ++l) {
						_coeff[i][j][k].push_back(0.);
					}
				}
			}
		}
	}

	/* *******************************************************
	*
	*	Tensor3222
	*
	*********************************************************/
	Tensor3222::Tensor3222 () {
		for (int i = 0; i < 3; ++i) {
			_coeff.push_back(vector<vector<vector<double> > > (2) );
			for (int j = 0; j < 2; ++j) {
				_coeff[i].push_back(vector<vector<double> > (2) );
				for (int k = 0; k < 2; ++k) {
					_coeff[i][j].push_back(vector<double> (2) );
					for (int l = 0; l < 2; ++l) {
						_coeff[i][j][k].push_back(0.);
					}
				}
			}
		}
	}

};//mechanics
