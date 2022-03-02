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
 *       $Id: fset.cpp 17611 2014-10-17 13:20:41Z pradal $
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




#include <iostream>

#include "header.h"
#include "fset.h"

using namespace std;

//static const char rcsid[] = "$Id: fset.cpp 17611 2014-10-17 13:20:41Z pradal $";

//------------- FSetArray --------------


FSetArray::FSetArray():  _MAXSIZE(0), _FNB(0) {

  _f = 0;
  _size = 0; // Aucun element n'est encore dans le tableau

}

// a fset is an array of features whose first element contains a line number

FSetArray::FSetArray(int size, int fnb):  _MAXSIZE(size*(fnb)), _FNB(fnb) {

  _f = new Feature[size*(fnb)];
  _size = 0; // Aucun element n'est encore dans le tableau

}

FSetArray::FSetArray(const FSetArray& array):  _MAXSIZE(array._MAXSIZE) {

  _f = new Feature[array._MAXSIZE];
  assert(_f);

  _size = array._size;

  for(int i=0; i<_MAXSIZE; i++) {

    _f[i] = *(array._f+i);

  }

}


FSetArray& FSetArray::operator=(const FSetArray& array) {

  if (this != &array) {

    _MAXSIZE = array._MAXSIZE;

    delete [] _f;
    _f = new Feature[array._MAXSIZE];

    assert(_f);

    _size = array._size; // Aucun element n'est encore dans le tableau

    for(int i=0; i<_MAXSIZE; i++) {

      _f[i] = *(array._f+i);

    }
  }

  return *this;

}

FSetArray::~FSetArray() {

  delete [] _f;

}


void FSetArray::resize(int size, int fnb) {

  int minsize = min(_MAXSIZE, size*(fnb));

  _MAXSIZE = size*(fnb);
  _FNB = fnb;

  Feature* oldf = _f;

  _f = new Feature[_MAXSIZE];

  assert(_f);

  _size = minsize;

  if (oldf) {

    for(int i=0; i<minsize; i++) _f[i] = oldf[i];

    delete [] oldf;

  }

}

void FSetArray::resize(int size) {

  resize(size, _FNB);

}

AmlBoolean FSetArray::storeFeature(FSetId fsetid, int findex, const Feature& f) {

  if (isValidIndex(fsetid+findex))  {
    _f[fsetid+findex] = f;
    return TRUE;
  }
  else return FALSE;

}

FSetId FSetArray::addFSet() {

  if (_FNB) {
    if (isValidIndex(_size+_FNB)) {
      for(int i=0; i<_FNB; i++) {
        _f[_size++].i = (unsigned long)LUNDEF;  // Tous les champs sont mis a UNDEF a l'initialisation
      }
      return _size-_FNB; // pour se repositionner au debut de l'ensemble
    }
    else {
      resize(_size*2);
      cerr << "WARNING: Redimensioning the number of features: " << _MAXSIZE << " to " << _MAXSIZE*2 << endl;
      assert(isValidIndex(_size+_FNB));
      for(int i=0; i<_FNB; i++) {
        _f[_size++].i = (unsigned long)LUNDEF;
      }
      return _size-_FNB; // pour se repositionner au debut de l'ensemble
    }
  }
  else return UNDEF; // si pas de colonnes on retourne Ok.

}

FSetId FSetArray::addFSet(const Feature* fid) {

  if (_FNB) {
    if (isValidIndex(_size+_FNB)) {
      for(int i=0; i<_FNB; i++) {
        _f[_size++] = fid[i];
      }
      return _size-_FNB; // pour se repositionner au debut de l'ensemble
    }
    else {
      resize(_size*2);
      cerr << "WARNING: Redimensioning the number of features: " << _MAXSIZE << " to " << _MAXSIZE*2 << endl;
      assert(isValidIndex(_size+_FNB));
        for(int i=0; i<_FNB; i++) {
          _f[_size++] = fid[i];
        }
        return _size-_FNB; // pour se repositionner au debut de l'ensemble
    }
  }
  else return UNDEF;

}
