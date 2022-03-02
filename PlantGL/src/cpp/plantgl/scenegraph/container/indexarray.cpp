/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: The Plant Graphic Library
 *
 *       Copyright 1995-2007 UMR CIRAD/INRIA/INRA DAP 
 *
 *       File author(s): F. Boudon et al.
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




#include "indexarray.h"
PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

/* ----------------------------------------------------------------------- */


Index3Array::Index3Array( uint_t size, const Index3& defaultvalue ) :
  Array1<Index3>(size,defaultvalue) {
}

Index3Array::~Index3Array( ) {
}

bool Index3Array::isValid( ) const {
  for (const_iterator _i = __A.begin(); _i != __A.end(); _i++)
    if (! _i->isUnique()) return false;
  return true;
}

uint_t * Index3Array::data( ) const {
  if(__A.empty())return NULL;
  uint_t * res = new uint_t[__A.size()*3];
  size_t _j = 0;
  for (const_iterator _i = __A.begin(); _i != __A.end(); _i++)
    { res[_j] = _i->getAt(0); _j++;
	  res[_j] = _i->getAt(1); _j++; 
	  res[_j] = _i->getAt(2); _j++;  }
  return res;
}

/* ----------------------------------------------------------------------- */


Index4Array::Index4Array( uint_t size, const Index4& defaultvalue ) :
  Array1<Index4>(size,defaultvalue) {
}

Index4Array::~Index4Array( ) {
}

bool Index4Array::isValid( ) const {
  for (const_iterator _i = __A.begin(); _i != __A.end(); _i++)
    if (! _i->isUnique()) return false;
  return true;
}


Index3ArrayPtr Index4Array::triangulate( ) const {
  Index3ArrayPtr _index3List(new Index3Array(__A.size() * 2));
 
  Index3Array::iterator _i3 = _index3List->begin();
  for (const_iterator _i4 = __A.begin(); _i4 != __A.end(); _i4++) {
    *(_i3++) = Index3(_i4->getAt(0),_i4->getAt(1),_i4->getAt(2));
    *(_i3++) = Index3(_i4->getAt(0),_i4->getAt(2),_i4->getAt(3));
  };

  return _index3List;
};  

uint_t * Index4Array::data( ) const {
  if(__A.empty())return NULL;
  uint_t * res = new uint_t[__A.size()*4];
  size_t _j = 0;
  for (const_iterator _i = __A.begin(); _i != __A.end(); _i++)
    { res[_j] = _i->getAt(0); _j++;
	  res[_j] = _i->getAt(1); _j++; 
	  res[_j] = _i->getAt(2); _j++; 
	  res[_j] = _i->getAt(3); _j++;  }
  return res;
}

/* ----------------------------------------------------------------------- */


IndexArray::IndexArray( uint_t size, const Index& defaultvalue  ) :
  Array1<Index>(size,defaultvalue) {
}

/** Constructs an IndexArray from an Index3Array.
    \post
    - \e self is valid. */
IndexArray::IndexArray( const Index3Array& array ) :
  Array1<Index>(array.size(),Index(3)) {
	  Array1<Index>::iterator it = begin();
	  for(Index3Array::const_iterator it2 = array.begin(); it2 != array.end(); ++it,++it2)
	  {
		  it->setAt(0,it2->getAt(0));
		  it->setAt(1,it2->getAt(1));
		  it->setAt(2,it2->getAt(2));
	  }
}

/** Constructs an IndexArray from an Index4Array.
    \post
    - \e self is valid. */
IndexArray::IndexArray( const Index4Array& array ) :
  Array1<Index>(array.size(),Index(4)) {
	  Array1<Index>::iterator it = begin();
	  for(Index4Array::const_iterator it2 = array.begin(); it2 != array.end(); ++it,++it2)
	  {
		  it->setAt(0,it2->getAt(0));
		  it->setAt(1,it2->getAt(1));
		  it->setAt(2,it2->getAt(2));
		  it->setAt(3,it2->getAt(3));
	  }
}

IndexArray::~IndexArray( ) {
}

bool IndexArray::isValid( ) const {
  for (const_iterator _i = __A.begin(); _i != __A.end(); _i++)
    if (! _i->isUnique()) return false;
  return true;
}


Index3ArrayPtr IndexArray::triangulate( ) const {
  uint_t _size = 0;

  for (const_iterator _i4f = __A.begin(); _i4f != __A.end(); _i4f++)
    if(_i4f->size() >= 3)_size += _i4f->size() - 2;
  
  Index3ArrayPtr _index3List(new Index3Array(_size));
 
  Index3Array::iterator _i3 = _index3List->begin();
  for (const_iterator _i4 = __A.begin(); 
		_i4 != __A.end(); 
		_i4++) {
	_size = _i4->size();
	if(_size >= 3)
    for (Index::const_iterator _i = _i4->begin() + 1; 
	 _i != _i4->end() - 1; 
	 _i++){
      (*_i3) = Index3(_i4->getAt(0), (*_i), (*(_i + 1)));_i3++;
	 }
  };

  return _index3List;
};  

void IndexArray::setAt(uint_t i, const Index3& t ) {
    Index t2(3);
    t2.setAt(0,t.getAt(0));
    t2.setAt(1,t.getAt(1));
    t2.setAt(2,t.getAt(2));
    Array1<Index>::setAt(i,t2);
}

void IndexArray::setAt(uint_t i, const Index4& t ) {
    Index t2(4);
    t2.setAt(0,t.getAt(0));
    t2.setAt(1,t.getAt(1));
    t2.setAt(2,t.getAt(2));
    t2.setAt(3,t.getAt(3));
    Array1<Index>::setAt(i,t2);
}

void IndexArray::setAt(uint_t i, const Index& t ) {
    Array1<Index>::setAt(i,t);
}

uint_t * IndexArray::data( ) const {
  size_t _size = 0;
  for (const_iterator _i4f = __A.begin(); _i4f != __A.end(); _i4f++)
    _size += _i4f->size();
  if(__A.empty())return NULL;

  uint_t * res = new uint_t[__A.size()];
  size_t _k = 0;
  for (const_iterator _i = __A.begin(); _i != __A.end(); _i++)
	for (Index::const_iterator _j = _i->begin(); _j != _i->end(); _j++)
    { res[_k] = *_j; _k++; }
  return res;
}

/* ----------------------------------------------------------------------- */

