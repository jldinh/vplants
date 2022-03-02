/* -*-c++-*- 
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture 
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): Ch. Godin (christophe.godin@cirad.fr) 
 *
 *       $Source$
 *       $Id: paramgeomcomputer.cpp 3261 2007-06-06 13:44:02Z dufourko $
 *
 *       Forum for AMAPmod developers    : amldevlp@cirad.fr
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





#include "aml/ammodel.h"
#include "aml/array.h"

#include "geomcomputer.h"

#include "plant.h"

//#include "Symbol/point.h"

/*!
  This function should compute the geometric models of 
  each vertices
*/

void CoordGeom::estimateParametricModels()
{

#ifndef SYSTEM_IS__IRIX


/*  IntType nb_branches=_plant->nbBranches();
  
  
  double * DistanceTable[nb_branches];
   

    for (size_t i=0;i<nb_branches;i++) {
      
	Branch branch = *_plant->_branches->at(i); // ieme branch
	
	if (branch.getSupport()==UNDEF) {
      
	}
	
	
	size_t nb_element=branch.branchComponents().entries();
	
	BranchElement br_el;
	
	for(size_t j=0;j<nb_element;i++){
	    
	    br_el = branch.branchComponents().at(j);
	    
	    vector<Point3> myPoints(1);
	    
	    VId v = br_el.getVertex();
      	    AMObj amla1 = (*_digitizedf)(v);
	    
	    if (amla1.tag == AMObjType::ARRAY) {

		Array* array1 = (Array*)(amla1.val.p);
		ArrayIter* pnext = array1->iterator();
		ArrayIter& next = *pnext;

		double myPoint[3];
	    
		while(next()) {
		    if (next.key().tag == AMObjType::ARRAY) {
			
			Array* array2 = (Array*)(next.key().val.p);
			ArrayIter* pnext2 = array2->iterator();
			ArrayIter& next2 = *pnext2;
			int numcoord=0;
			while(next2()) {
			    if (next2.key().tag == AMObjType::REAL){
				numcoord++;
				myPoint[numcoord]= next2.key().val.r;
			    }
			    else cerr << "!!! Non real_t value returned by function 'digitized'" << endl;
			}
			if(numcoord!=3)
			    cerr << "!!! Non 3D Point value returned by function 'digitized'" << endl;
			else myPoints.push_back(Point3((Real)myPoint[0],(Real)myPoint[1],(Real)myPoint[2]));
			delete pnext2;
		    }
		}
		delete pnext;
		
	    }
	    else {

	    }

	}*/
      
/*	VId father=_plant->topoFather(br_el.getVertex(),ANY);   
	
	if (father==UNDEF) {
	
	}  
	else {
	    VIdList* list=_plant->topoSons(father,PLUS);
	    IntType nb=list->entries();
	}
	
    }*/
  
  // pour enregistrer le modele geometrique calcule:
  // br_el._psymbol = SymbolPtr(...);
  
#else

  cerr << "!!!!!!! Not implemented on SGI / IRIX" << endl;

#endif


}


