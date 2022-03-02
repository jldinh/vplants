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
 *       $Id: branch.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef SAMIR_BRANCH_DEF
#define SAMIR_BRANCH_DEF

#include "tool/rw_vector.h"
#include "tool/rw_stack.h"
#include "tool/rw_slist.h"
#include "tool/rw_list.h"

#include "vector.h"
#include "definitions.h"

// OLD INCLUDES
//#include "GEOM/geom_geometry.h"
#include "plantgl/pgl_geometry.h"
PGL_USING_NAMESPACE

class BranchElement
{
 public:

  // Selectors

  ValType getLength() const { return _length; };
  ValType getTopDia() const { return _topdia; };
  ValType getBotDia() const { return _botdia; };
  MyVector getDirp() const { return _dirp; };
  MyVector getDirs() const { return _dirs; };
  MyVector getDirt() const { MyVector _dirt(_dirp*_dirs); _dirt.norm(); return _dirt;}
  MyVector getOrigin() const { return _origin; };
  ValType getAlpha() const { return _alpha; };
  ValType getBeta() const { return _beta; };
  VId getVertex() const { return _vertex; };

  // Modificators

  void putLength(const ValType);
  void putTopDia(const ValType);
  void putBotDia(const ValType);
  void putVertex(const VId);
  void putDirp(const MyVector);
  void putDirs(const MyVector);
  void putDirt(const MyVector);
  void putOrigin(const MyVector);
  void putAlpha(const ValType);
  void putBeta(const ValType);

  // Operators

  AmlBoolean operator==(const BranchElement&) const;
  const BranchElement& operator=(const BranchElement&);

  // Test the element

  AmlBoolean isValid() const;

  // Constructors

  BranchElement(const BranchElement& );
  BranchElement(const ValType length,
                const ValType alpha,
                const ValType beta,
                const ValType botdia,
                const ValType topdia,
                const VId vertex);

  BranchElement(const VId vertex);

  BranchElement();
  ~BranchElement();

  // Destructor

  //~BranchElement();


  // Debug

  void report() const;


#ifndef SYSTEM_IS__IRIX

  // used only in the case where the user wants to compute parametric models
  // like NURBS, BEZIER, etc. This penalizes the other cases a lot
  // by adding a useless field !!!!! Should be changed

  GeometryPtr _psymbol;

#endif

 private:

  ValType _length;
  ValType _topdia;
  ValType _botdia;
  ValType _alpha;
  ValType _beta;
  ValType _gamma;
  VId  _vertex;
  MyVector _dirp;
  MyVector _dirs;
  MyVector _origin;


};

typedef RWTValDlist<BranchElement>  BranchCompoList;

bool contains(const BranchCompoList& l, VId v);

class Branch
{
  friend class Azimut;
  friend class Diameters;
  friend class Coordinates;
  friend class Length;
  friend class Dresser;
  friend class Alpha;
  friend class RequiredCoords;
  friend class CoordLength;
  friend class Plant;
  friend class VirtualElements;

 public:

  Branch(const VId support, IntType plant_number=0);
  Branch(const Branch& );
  ~Branch();

  const Branch& operator=(const Branch&);
  AmlBoolean operator==(const Branch& ) const;
  AmlBoolean operator<(const Branch& ) const;

  void addElement(const BranchElement ); // Adds a new element to the branch.
  const BranchCompoList& branchComponents() const;

  VId baseOfBranch() const;
  VId endOfBranch() const;

  VId getSupport() const;
  VId getBranchId() const { return _branchId; };

  IntType getCategory() const {return _category;};

  void putCategory(IntType);


 private:

  IntType _category;
  VId _support;
  ValType _alpha; // Insertion angle
  ValType _beta;  // Phyllotaxy
  BranchCompoList* _components;
  LongType _branchId;
  IntType _plantNumber;
  static LongType _branchCounter;

};



typedef RWTPtrSortedVector<Branch> Ramifications;
typedef RWTStack< VId,RWTValDlist<VId> > BranchStack;
typedef RWTQueue< VId,RWTValDlist<VId> > BranchQueue;

#endif
