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
 *       $Id: fset.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef FSET_HEADER
#define FSET_HEADER

#include <assert.h>

#include "aml/defs.h"

// Le FSetArray est un tableau de Feature
// un ensemble de features associees a un vertex est un FSet.
// Un tel ensemble comporte FSetDef::FNb() Features. Chaque
// Features a bien entendu une taille fixe (cf def.h)
// 
// La premiere feature sert (en general) a stocker le numero de ligne (fset[0]).
// Les autres servent a stocker les features declarees par l'utilisateur:
// donc de 1 a FNb() compris.
//
// Pour augmenter le tableau des feature sets on doit donner un
// tableau de FNb() Features.

class FSetArray{

  int _MAXSIZE;			//  _MAXSIZE Features in this array
  int _FNB;			// total nb of features in an fset
  int _size;			// fset nb in the array

  Feature* _f;
  
  AmlBoolean isValidIndex(FSetId i) const {if (i<_MAXSIZE && i>0) return TRUE; else return FALSE;}

public:

  FSetArray();

  FSetArray(int size, int fnb);
  FSetArray(const FSetArray&);
  ~FSetArray();

  void resize(int size, int fnb);
  void resize(int size);

  int entries() const {return _size;}

  int capacity() const {return (_FNB) ?  (_MAXSIZE/_FNB): 0;} 
  int featNbPerFSet() const {return _FNB;}

  FSetArray& operator=(const FSetArray&);
  
  int length() const {return _size;} // total length in Features
  int fsetLength() const {return (_FNB) ? (_size / _FNB) : 0;} // total length in FeatureSets
  
  AmlBoolean storeFeature(FSetId fsetid, FId findex, const Feature& f);

  FSetId addFSet(); // cree un ensemble vierge de features
  FSetId addFSet(const Feature*); // cree un "ensemble de features" par copie

  Feature* operator[](FSetId i) {return _f+i;}
  Feature& operator()(FSetId i, FId j) {assert(j>=0); return *(_f+i+j);}   
  const Feature& operator()(FSetId i, FId j) const {assert(j>=0); return *(_f+i+j);}   

};

#endif

