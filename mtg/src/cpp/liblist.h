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
 *       $Id: liblist.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _LIB_LIST_SAMIR_DEF_
#define _LIB_LIST_SAMIR_DEF_

#include "definitions.h"
#include "tool/rw_vector.h"
//#include <rw/tvsrtvec.h>

class LibElement
{
 public:

  LibElement(char,ValType);
  LibElement(char);
  LibElement(const LibElement&);
  LibElement();

  AmlBoolean operator==(const LibElement&) const;
  const LibElement& operator=(const LibElement&);
  AmlBoolean operator<(const LibElement&) const;

  ValType getValue() const { return _value; };
  char getSymbol() const { return _symbol; };

 private:

  ValType _value;
  char _symbol;
};

typedef RWTValSortedVector<LibElement> LibList;

#endif
