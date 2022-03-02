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
 *       $Id: amobjtable.cpp 17611 2014-10-17 13:20:41Z pradal $
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




#include "amobjtable.h"


AMObj* AMObjTable::insert(const RWCString& key, const AMObj& data) {

  AMObj item;

  if (findValue(key, item)) {

    /*
    if (item.type() != AMObjType::FNODE) {
      cerr << "Warning : the variable : " << key << " already referred to an object." << endl;
      cerr << "This object has been overwritten by the new one." << endl;
    }
    else {
      cerr << "Warning : the function : " << key << " already referred to an object." << endl;
      cerr << "This object has been overwritten by the new one." << endl;
    }
    */
    
  }

  AMObj& psr = (*this)[key];

  psr = data;

  return &psr;

}


AmlBoolean AMObjTable::isValueIn(const AMObj& item) const {

  AMObjTableIter next(*(AMObjTable*)this);

  while(next()) {

    if (next.value() == item) return TRUE;

  }

  return FALSE;
}



