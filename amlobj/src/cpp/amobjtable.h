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
 *       $Id: amobjtable.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef AMOBJTABLE_HEADER
#define AMOBJTABLE_HEADER

#include "tool/rw_hdict.h"
//#include <rw/tvhdict.h>

#include "amobj.h"

typedef RWTValHashDictionaryIterator<RWCString, AMObj> AMObjTableIter;

class AMObjTable : public RWTValHashDictionary<RWCString, AMObj> {

public:

  AMObjTable(size_t (*hashfunc)(const RWCString&)): RWTValHashDictionary<RWCString, AMObj>(hashfunc) {}

  AMObj* insert(const RWCString& key, const AMObj& data);
  AmlBoolean isValueIn(const AMObj& item) const;

};


#endif
