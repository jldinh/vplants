#ifndef CPL
#define CPL
#endif
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
 *       $Id: edge.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef EDGE_HEADER
#define EDGE_HEADER

#include <iostream>

#include "tool/rw_list.h"
//#include <rw/tvslist.h>

#ifndef CPL
#include "aml/defs.h"
#else
#include "bitvec.h"
#endif

typedef RWTValDlist<EId> EIdList;

// Une edge n'a que un vertex father et un vertex cible.
// Dans le cas general, une edge peut avoir plusieurs explications
// a l'echelle superieure et plusieurs interpretations a l'echelle
// inferieure (explications et interpretaions sont egalement des Edges).

class Edge {

  friend std::ostream& operator<<(std::ostream&, const Edge&);

  EId _eid;
  EType _etype;

  VId _son;
  VId _father;

public:

  Edge();
  Edge(EId eid, EType etype, VId son, VId father);
  Edge(const Edge&);
  ~Edge();

  int binaryStoreSize() const;

  Edge& operator=(const Edge&);
  AmlBoolean operator==(const Edge&) const;

  EId eid() const {return _eid;}
  EType type() const {return _etype;}

  VId son() const {return _son;}
  VId father() const {return _father;}

  void setSon(VId x) {_son = x;}
  void setFather(VId x) {_father = x;}

  std::ostream& print(std::ostream&) const;
  std::ostream& printAll(std::ostream&) const;

};

std::ostream& operator<<(std::ostream& o, const Edge& obj);

#endif
