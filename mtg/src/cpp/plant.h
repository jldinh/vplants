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
 *       $Id: plant.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _EVOPLANT_SAMIR_DEF_
#define _EVOPLANT_SAMIR_DEF_

#include "tool/rw_queue.h"
#include "tool/rw_list.h"
// #include <rw/tvsrtvec.h>
//#include <rw/tqueue.h>
//#include <rw/tpslist.h>
#include "definitions.h"
#include "branch.h"
#include "vector.h"
#include "mynode.h"
#include <stdio.h>

const IntType MAXSEARCH=3;

class PlantFrame;

//typedef RWTValSortedVector<VId> ComponentsList;

class Plant
{
  friend class StandardGeom;
  friend class Azimut;
  friend class Diameters;
  friend class Coordinates;
  friend class Dresser;
  friend class RequiredCoords;
  friend class CoordGeom;
  friend class VirtualElements;

 public:

  // The constructor build the frame of the plant

  Plant(MTG* mtg,
        PlantFrame*,
        VId vertex,
        EType default_edge,
        IntType level,
        Options opt,
        ValType* translation=NULL,
        ValType* origine=NULL);

  Plant(MTG* mtg,
        PlantFrame*,
        const VIdList* vid_list,
        EType default_edge,
        IntType level,
        Options opt,
        ValType* translation=NULL,
        ValType* origine=NULL);

  virtual ~Plant();

  const Branch& findBranch(size_t) const;

  size_t nbBranches() const { return _branches->entries(); };

  MyVector minPoint() const { return _minpoint; };
  MyVector maxPoint() const { return _maxpoint; };
  LongType getPlantId() const { return _plantId; };
  IntType getPlantCounter() const { return _plantCounter; };


  AmlBoolean operator==(const Plant&) const;

  BranchElement searchForElement(VId vertex) const;

  MTG* getMtg();
  const MTG* getMtg() const;

  AmlBoolean isAValidPlant() const {return _isValid;};


  // Methods for mtg exploring.

  virtual VIdList* sons(VId, EType) const;
  virtual VId topoFather(VId,EType) const;
  virtual EType edgeType(VId, VId ) const;
  virtual VId findLocalTopoRoot(VId, EType) const;
  virtual VIdList* topoSons(VId, EType) const;
  virtual IntType vscale(VId) const;
  virtual IntType pathLength(VId,VId,EType) const;
  virtual VId location(VId) const;
  virtual VIdList* compoSons(VId) const;
  virtual VIdList* compoSons(VId, IntType ) const;

  virtual int featureNb() const { return _mtg->featureNb();};
  virtual FType fType(int index) const { return _mtg->fType(index);};
  virtual String fname(int index) const { return _mtg->fname(index);};
  virtual VId compoFather(VId vertex) const { return _mtg->compoFather(vertex);};
  virtual VId compoFather(VId vertex,int level) const { return _mtg->compoFather(vertex,level);};
  virtual char symbol(VId vertex) const { return _mtg->symbol(vertex);};
  virtual VId mtgRoot() const { return _mtg->mtgRoot();};
  virtual int vindex(VId vertex) const { return _mtg->vindex(vertex);};
  virtual const Feature* feature(VId v, FIndex i, Date d) const { return _mtg->feature(v,i,d);};
  virtual Date lastDate(VId v) const { return _mtg->lastDate(v);};
  virtual AmlBoolean hasFeatures(VId v) const { return _mtg->hasFeatures(v);};
  virtual VId mtgTopoFather(VId v, EType edge) const { return _mtg->topoFather(v,edge);};
  virtual VId mtgTopoFather(VId v) const { return _mtg->topoFather(v,ANY);};

  const IntType getLevel(){
      return _level;
  }

  void report();
  void testSons();

  PlantFrame* _plantframe;

  VIdList* _root_list; // stores the array of root vertices when several plants must be plotted

  MyVector* _translation;
  ValType* _origin;

  Ramifications* _branches;

 protected:

  VId _vertex;
  IntType _level;
  IntType _entitiesNumber;
  //ComponentsList* _components;
  VIdList* _components;
  MTG* _mtg;
  MyVector _minpoint;
  MyVector _maxpoint;
  LongType _number;
  MyTree* _myTree;
  EType _defaultEdge;
  AmlBoolean _isValid;
  LongType _plantId;
  AmlBoolean _isSympodial;


  static LongType _plantNumber;

  virtual VIdList* lookForComponents(VId, IntType);
  virtual VIdList* lookForComponents(const VIdList*, IntType);

  virtual VIdList* theRoots(VId,IntType);

  void lookForBranches(VId);
  void lookForFather(MyNode&);
  void buildMyTree();
  void buildSympodialTree();
  AmlBoolean areEqualLists(VIdList*,VIdList*);
  void compare();

 private:

  static IntType _plantCounter;

};

typedef RWTPtrDlist<Plant> PlantList;

#endif
