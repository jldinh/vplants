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
 *       $Id: edge.cpp 17611 2014-10-17 13:20:41Z pradal $
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




#include "edge.h"

using namespace std;

typedef RWTValDlistIterator<EId>        EIdListIter;

//static const char rcsid[] = "$Id: edge.cpp 17611 2014-10-17 13:20:41Z pradal $";

Edge::Edge() {

  _eid = UNDEF;
  _etype = ANY;
  _son = _father = UNDEF;

}

Edge::Edge(EId eid, EType etype, VId son, VId father) {

  _eid = eid;
  _etype = etype;
  _son = son;
  _father = father;

}


Edge::Edge(const Edge& edge) {

  if (this != &edge) {

    _eid = edge._eid;
    _etype = edge._etype;
    _son = edge._son;
    _father = edge._father;

  }

}



Edge::~Edge() {

}

int Edge::binaryStoreSize() const {

  int count = sizeof(_eid) +
              sizeof(_etype) +
              sizeof(_son) +
              sizeof(_father);

  return count;

}


Edge& Edge::operator=(const Edge& edge) {

  if (this != &edge) {

    _eid = edge._eid;
    _etype = edge._etype;
    _son = edge._son;
    _father = edge._father;

  }

  return *this;

}

AmlBoolean Edge::operator==(const Edge& edge) const{

  if (this == &edge) return TRUE;
  else if (_eid == edge._eid) return TRUE;
  else return FALSE;

}

ostream& Edge::print(ostream& o) const {

  o << " eid = " << _eid << ", father = " << _father << ", son = "
  << _son << ", type = " << _etype << endl;

  return o;

}

ostream& Edge::printAll(ostream& o) const {

  print(o);

  return o;

}


ostream& operator<<(ostream& o, const Edge& obj){

  return obj.print(o);

}

