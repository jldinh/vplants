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
 *       $Id: refsystem.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include <assert.h>
#include <math.h>
#include <iostream>
#include "refsystem.h"


// Compute the coordinates of the triangle {A, B, C}
// where the origin is A and the abscisse axis is along AB.

TriangRefSystem::TriangRefSystem(ValType _lab, ValType _lac, ValType _lbc) : RefSystem() {

  lab = _lab;
  lac = _lac;
  lbc = _lbc;

  lab2 = lab*lab;
  lac2 = lac*lac;
  lbc2 = lbc*lbc;

  cosA = (lac2+lab2-lbc2)/(2*lab*lac);
  sinA = sqrtf(1-cosA*cosA);

  //cerr << "angle (AB, AC) = " << MyAcos(cosA) << " rad" << endl;

 // ptA.x = 0.0;
 // ptA.y = 0.0;
 // ptA.z = 0.0;

 // ptB.x = lab;
 // ptB.y = 0.0;
 // ptB.z = 0.0;

 // ptC.x = lac*cosA;
 // ptC.y = lac*sinA;
 // ptC.z = 0.0;
  
  ptA=MyVector (0,0,0);
  ptB=MyVector (lab,0,0);
  ptC=MyVector (lac*cosA,lac*sinA,0);

  //cerr << "pt A = {" << ptA[0] << "," << ptA[1] << "," << ptA[2] << "}" << endl;
  //cerr << "pt B = {" << ptB[0] << "," << ptB[1] << "," << ptB[2] << "}" << endl;
  //cerr << "pt C = {" << ptC[0] << "," << ptC[1] << "," << ptC[2] << "}" << endl;

}

AmlBoolean TriangRefSystem::findPoint(ValType la, ValType lb, ValType lc, MyVector& p) const {

  int above = 1;
  if (la < 0) {

    assert(lb<0);
    assert(lc<0);
    above = 0;
    
    la = -la;
    lb = -lb;
    lc = -lc;

  }

  ValType la2 = la*la;
  ValType lb2 = lb*lb;
  ValType lc2 = lc*lc;
  ValType Lab2 = (lab2+la2-lb2)/2; // can be negative
  ValType Lac2 = (lac2+la2-lc2)/2; // can be negative
  // ValType cosbeta = Lab2/(lab*la);
  // ValType cosgamma = Lac2/(lac*la);
  ValType x,y,z;

  x = Lab2/lab;
  y = (Lac2/lac - cosA*Lab2/lab)/sinA;
 
  ValType lah2 = x*x + y*y;
  
  if (la2-lah2 < 0) {
    // cerr << "\n*** ERROR : la2 - lah2 < 0 : " << la2-lah2 << endl;
    z = MySqrt(lah2-la2);
    p=MyVector(x,y,z);
    return 0;
  }
  else z = MySqrt(la2-lah2);

  if (!above) z = - z;

  p=MyVector(x,y,z);

  return 1;

}


AmlBoolean CartesianRefSystem::findPoint(ValType x, ValType y, ValType z, MyVector& v) const
{ 
  
  v=MyVector(x,y,z);
  
  return 1;
}
