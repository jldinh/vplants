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
 *       $Id: utils_template.cpp 3258 2007-06-06 13:18:26Z dufourko $
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




#ifndef UTILS_TEMPLATE_DEFINITION
#define UTILS_TEMPLATE_DEFINITION

// Cf C++ Language Overview p 8-6 et 8-7
// NE DOIT PAS INCLURE LE HEADER !!

// #include "utils_template.h"

template <class T>
TwoDimArray<T>::TwoDimArray(int dim1, int dim2) {
  
  _dim1 = dim1;
  _dim2 = dim2;
  if(dim1>0 && dim2>0) _t = new T[dim1*dim2];
  else _t = NULL;

}

template <class T>
TwoDimArray<T>::TwoDimArray(const TwoDimArray<T>& xt) {
  
  _dim1 = xt._dim1;
  _dim2 = xt._dim2;
  if(_dim1>0 && _dim2>0) _t = new T[_dim1*_dim2];
  else _t = NULL;

  for(int i=0; i<_dim1; i++) {
    for(int j=0; j<_dim1; j++) {
      (*this)(i,j) = xt(i,j);
    }
  }
}

template <class T>
TwoDimArray<T>::~TwoDimArray() {

  delete [] _t;

}


template <class T>
TwoDimArray<T>& TwoDimArray<T>::operator=(const TwoDimArray<T>& xt) {
  
  if (this != &xt) {
    
    _dim1 = xt._dim1;
    _dim2 = xt._dim2;
    if(_dim1>0 && _dim2>0) _t = new T[_dim1*_dim2];
    else _t = NULL;
    
    for(int i=0; i<_dim1; i++) {
      for(int j=0; j<_dim1; j++) {
	(*this)(i,j) = xt(i,j);
      }
    }
  }

  return *this;

}

#endif
