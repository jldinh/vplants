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
 *       $Id: linetree.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef SAMIR_LINETREE_DEF
#define SAMIR_LINETREE_DEF

//#include <rw/rwfile.h>
#include <fstream>

#include "definitions.h"
#include "vector.h"
#include "plant.h"
#include "color.h"
#include "symbol.h"
#include "correlement.h"

#include "dresser.h"
#include "virtualelements.h"

//#include "quotientgeometrycomputer.h"
class QuotientGeometryComputer;

//#include "GEOM/scne_scene.h"
#include "plantgl/pgl_scene.h"

PGL_BEGIN_NAMESPACE

class Discretizer;
class Material;
typedef RCPtr<Material> MaterialPtr;

PGL_END_NAMESPACE

#include <vector>

typedef std::vector<Shape> ShapeVector;

#include "aml/fnode.h"



/*

   Compiled on 28 July.
   0 errors.
   3 warnings.

*/

/*
typedef struct {

  SymbType symbol;
  LongType val1;
  LongType val2;
  LongType range;
  ValType matrix[3][4];
  ValType base_dia;
  ValType sommit_dia;
  LongType entity_number;

} LineRecord;  */


/* ----------------------------------------------------------------------- */


typedef struct {

  long symbol;
  long val1;
  long val2;
  long range;
  real_t matrix[3][4];
  real_t base_dia;
  real_t sommit_dia;
  long entity_number;

} LineRecord;


/* ----------------------------------------------------------------------- */


class LineTree : public AMModel
{

  friend class Dresser;
  friend class VirtualElements;

 private:

  /// Virtual Elements

  AmlBoolean _areLeaves;
  AmlBoolean _areFlowers;
  AmlBoolean _areFruits;

  VirtualElements *_virtualLeaves, *_virtualFruits, *_virtualFlowers;

  void makeVirtualFruits(VirtualElements*);
  void makeVirtualLeaves(VirtualElements*);
  void makeVirtualFlowers(VirtualElements*);

  // checks whether context for addition of virtual leaves is set
  AmlBoolean _isEnvironementSet;

  VirtualSymbolTable* _virtualTable;
  VId _vertexNumber;

  // Added set of virtual symbols;
  Branch *_addedBranch;
  // this "virtual" branch is the last branch of the set of branches
  // (of type Ramifications) stored in the object plant and
  // pointed to by the plantframe

  // GEOMETRY and APPEARANCE

  /// Scene of computed geometry.
  ScenePtr _scene;
  ShapeVector _base_symbol_list;
  /// default material is red.
  AppearancePtr _default_mat;

  Dresser* _dr;

  AMObj _plot() const;
  AMObj _plot(FNode* showMicro,FNode* showMacro) const;


  /// Quotient Geometry Computer.
  QuotientGeometryComputer* _qgc;

  // Functions computing the exact geometry and appearance of a vertex
  //
  // SymType symbol
  // the value return by the function is in the last argument (GeometryPtr&)

  bool geomptr(const BranchElement& branch_element,
               SymbType symbol,
               GeometryPtr& psmb,
               Discretizer & dis) const;

  bool matptr(VId vtx,
              SymbType symbol,
              MaterialPtr& pmat) const;


  AmlBoolean makeLigFile(const Plant&,
                      const char*,
                      const CorrTable&) const;

  AmlBoolean makeInfFile(const MyVector& min_MyVector,
                      const MyVector& max_MyVector,
                      const char*) const;

  AmlBoolean makeDtaFile(const ColorsTable&,
                      const SymbLib&,
                      const char*) const;

  /* AmlBoolean makeArcFile(const Plant&,
                      const char*); */

  /// Save LineTree as XML
  AmlBoolean saveAsXML(const char *) const;

  AmlBoolean _state;

  void writeRecord(const SymbType,
                   const LongType,
                   const LongType,
                   const MyVector,
                   const MyVector,
                   const MyVector,
                   const MyVector,
                   const ValType,
                   const ValType,
                   LineRecord&) const;

  void numberToString(IntType, char*) const;
  void numberToString(ValType, char*) const;

 public:

  LineTree(const char*,
           const PlantFrame*,
           Dresser*,
           VirtualElements*,
           VirtualElements*,
           VirtualElements*
           );

  ~LineTree();

  /// PlantFrame.
  const PlantFrame* _pf;

  int isValid() const {return _state;}

  VirtualSymbol getVirtualSymbol(VId vertex) const;

  AmlBoolean viewer(const FNode* filter, bool display_on);

  virtual AMObj display(std::ostream& o, const AMObjVector& args) const;
  virtual AMObj plot(GP_window&, const AMObjVector& args) const;

  virtual std::ostream& displayOneLine(std::ostream&) const;
  virtual AMObj extract(const AMObjVector& args) const;
  virtual AMObj save(const AMObjVector& args) const;
  VId fatherOfVirtualElement(const VId) const;
  VId complexOfVirtualElement(const VId, int s = -1) const;
  bool isVirtualElement(const VId) const;

  const ScenePtr&  getScene() const {
    return _scene;
  };

  const ScenePtr getMacroScene() const;


};

#endif



