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
 *       $Id: bitvec.cpp 3258 2007-06-06 13:18:26Z dufourko $
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

#include "bitvec.h"

using namespace std;

int BitVec::firstTrue() const {

  if (isClear()) return -1;
  else {
      int i;
          for (i=0; i<BITS(flags) && !isSet(i); i++);
      return i;
  }
}

int BitVec::nbBitsSet() const {

  int nb = 0;

  for (register int i=0; i<BITS(flags); i++) if (isSet(i)) nb++;

  return nb;

}

ostream& BitVec::print(ostream& o) const {

  for (register int i=0; i<BITS(flags); i++) {
    if (isSet(i)) o << '1';
    else o << '0';
  }

  return o;

}

BitVec operator&(const BitVec& fs1, const BitVec& fs2) {

  return (BITVECTYPE) (fs1.flags & fs2.flags);

}

BitVec operator|(const BitVec& fs1, const BitVec& fs2) {

  return (BITVECTYPE) (fs1.flags | fs2.flags);

}


ostream& operator<<(ostream& o, const BitVec& fs) {

  return fs.print(o);

}
