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
 *       $Id: mynode.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _SAMIRNODE_SAMIR_DEF_
#define _SAMIRNODE_SAMIR_DEF_

#include "definitions.h"
#include "tool/rw_vector.h"
//#include <rw/tpsrtvec.h>

class MyNode
{
 public:

  MyNode(VId);

  MyNode(VId,
        VId);

  MyNode(VId,
        VId,
        const VIdList*,
        const VIdList*);

  MyNode(const MyNode&);
  MyNode();
  ~MyNode();

  AmlBoolean operator<(const MyNode&) const;
  AmlBoolean operator==(const MyNode&) const;
  const MyNode& operator=(const MyNode&);

  void addLessSons(VId vertex);
  void addPlusSons(VId vertex);
  void addLessSons(const VIdList* list);
  void addPlusSons(const VIdList* list);
  void putFather(VId father);
  void putRelation(EType);

  VId getVertex() const {return _vertex;};
  VId getFather() const {return _father;};
  EType getRelation() const {return _relation;};

  VIdList* getLessSons() const {return new VIdList (*_lessSons);};
  VIdList* getPlusSons() const {return new VIdList (*_plusSons);};

 private:

  VIdList* _lessSons;
  VIdList* _plusSons;
  VId _father;
  VId _vertex;
  EType _relation;

  void clearAndDestroy();
  void construct(const MyNode&);

};

typedef RWTPtrSortedVector<MyNode> MyTree;

#endif
