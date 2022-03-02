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
 *       $Id: vtxinfo.cpp 3258 2007-06-06 13:18:26Z dufourko $
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




//#include <stream.h>
#include <assert.h>

#include "vtxinfo.h"
#include "error.h"

//static const char rcsid[] = "$Id: vtxinfo.cpp 3258 2007-06-06 13:18:26Z dufourko $";

using namespace std;

// ******************
//   CLASS VtxInfo
// ******************


VtxInfo::VtxInfo(int capacity):_vtx(capacity), _line(capacity) {

  _size = 0;

}

void VtxInfo::insert(int vtx, int line) {

  _vtx.insert(vtx);
  _line.insert(line);

  _size++;

}

int VtxInfo::findFirstLine(int vtx) const {

  // vtx might be a vertex just declared
  // Hence one should find the first vertex whose id
  // is greater than vtx and return the corresponding
  // line number.

  register int i;

  for(i=0; i<_size; i++) {

    if (_vtx[i] >= vtx) break;

  }

  if (i == _size) return UNDEF;
  else return _line[i];

}

int VtxInfo::findLastLine(int vtx) const {

  // vtx might be a vertex just declared
  // Hence one should find the first vertex whose id
  // is greater than vtx and return the corresponding
  // line number.

  register int i;

  for(i=0; i<_size; i++) {

    if (_vtx[i] >= vtx) break;

  }

  cerr << "i = " << i << ", size = " << _size << endl;

  if (i == _size) return UNDEF;
  else return _line[i];

}
