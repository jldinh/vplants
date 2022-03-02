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
 *       $Id: vector.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef SAMIR_VECTOR_DEF
#define SAMIR_VECTOR_DEF

#include <math.h>
#include "definitions.h"
#include "tool/rw_list.h"
//#include <rw/tvslist.h>
#include <stdio.h>

/*
  Compiled on 28 of July

   0 errors.
   0 warnings.

   Tested on the 28 July.

*/

class MyVector
{
 public:

  MyVector( const ValType,const ValType,const ValType );
  MyVector( const ValType,const ValType ); // Polars coordinates
  MyVector( const MyVector& );
  MyVector();

  const MyVector& operator=(const MyVector&);
  AmlBoolean operator==(const MyVector&) const;

  const ValType& operator[](const IntType index ) const;
  ValType& operator[](const IntType index ) ;
  MyVector operator+(const MyVector&) const;
  MyVector operator*(const MyVector&) const; // Vectorial
  ValType operator^(const MyVector&) const; // Scalar
  MyVector operator-(const MyVector&) const;

  void  changeRepere(const MyVector& u, const MyVector& v, const MyVector& w);
  // Recalcul les coordonnees par rapport au repere orthonorme.
  // Les anciennes coordonnees etaient par rapport au repere (o,u,v,w).

  void trafic(ValType);

  void multiply(const ValType );

  // MyVector& rotateX(ValType alpha);
  const MyVector& rotateY(const ValType alpha);
  const MyVector& rotateZ(const ValType alpha);

  // Angles A and B are the spherical coordinates of the vector:
  // A corresponds to the elevation angle (positive when going to positive Z)
  // B corresponds to the azimuth angle (in the plane XY, positive towards Y)

  ValType computeAlpha() const;
  ValType computeBeta() const;
  ValType computeLength() const;

  void norm();


  void report();

 private:

  ValType _x,_y,_z;

  void Test();

};

typedef RWTValDlist<MyVector> ListOfMyVectors;

#endif

