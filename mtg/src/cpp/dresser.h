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
 *       $Id: dresser.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _DRESSER_SAMIR_DEF_
#define _DRESSER_SAMIR_DEF_

#ifndef SYSTEM_IS__IRIX
// OLD INCLUDES
//#include "GEOM/geom_geometry.h"
//#include "GEOM/appe_appearance.h"
#include "plantgl/pgl_geometry.h"
#include "plantgl/pgl_appearance.h"
#endif

#include "tool/rw_slist.h"
//#include <rw/tvslist.h>

#include "definitions.h"
#include "symbol.h"
#include "correlement.h"
#include "color.h"
#include "branch.h"



class DressingFile;
class Plant;
class Dresser;
class LineTree;


class Painter
{
 public:

  Painter(MTG*,
          Plant*,
          Dresser*,
          const ColorLib&,
          const DressingFile* dressing_file);

  // Must have a constructor with a FNode function (for colors interpollation).

  ~Painter();

  void insertElement(LineTree*,
                     VId vertex,
                     ValType range=1);

  const ColorsTable& getColorsTable() const;
  const CorrTable& getCorrTable() const;

  void changeDressingFile(const DressingFile*, const ColorLib*);

  void setMinTreshold(ValType);
  void setMaxTreshold(ValType);
  void setMediumTreshold(ValType);
  void setInterpolFunction(FNode*);
  void setColorFunction(FNode*);
  void setColorRGBFunction(FNode*);
  void setMaterialFunction(FNode*);
  void setGeometryFunction(FNode*);
  void setSymbolFunction(FNode*);

  ValType fnodeValue(FNode* fnode_fun, VId argu);
  MyColor fnodeValueRGB(FNode* fnode_fun, VId argu);

  void adjustColors();

  MyColor computeColorForVirtualVertex(LineTree*, IntType);

  AppearancePtr computeMaterial(VId vtx) const;
  GeometryPtr computeGeometry(VId vtx) const;


 private:

  ColorsTable* _colorTable;
  MTG* _mtg;
  const ColorLib* _colorLib;
  CorrTable* _corrTable;
  const DressingFile* _dressingFile;
  Plant* _plant;
  Dresser* _dresser;
  FNode* _interpolFun;
  FNode* _colorFun;
  FNode* _colorRGBFun;
  FNode* _materialFun;
  FNode* _geometryFun;
  FNode* _symbolFun;
  ValType _maxTreshold;
  ValType _minTreshold;
  ValType _mediumTreshold;
  AmlBoolean _isInterpol, _isColor,_isColorRGB,_isMaterial,_isGeometry,_isSymbolFun;
  AmlBoolean _isMaxTreshold, _isMinTreshold, _isMediumTreshold;

  MyColor computeColor(VId vertex);

  ValType greenInterpol(ValType);
  ValType blueInterpol(ValType);
  ValType redInterpol(ValType);

};



class Dresser
{
 public:

  Dresser(Plant&,
          const DressingFile*);

  ~Dresser();

  const SymbLib& getSymbLib() const;
  const ColorsTable& getColorsTable() const;
  const CorrTable& getCorrTable() const;

  void makeInterpol(FNode* function);
  void makeColorFun(FNode* function);
  void makeColorRGBFun(FNode* function);
  void makeMaterialFun(FNode* function);
  void makeGeometryFun(FNode* function);
  void makeSymbolFun(FNode* function);
  void makeMaxTreshold(ValType);
  void makeMinTreshold(ValType);
  void makeMedium(ValType);

  void computeMinAndMax();
  void dressThePlant(LineTree*);

  void changeDressingFile(const DressingFile*);

  AppearancePtr computeMaterial(VId vtx) const {return _painter->computeMaterial(vtx);}
  GeometryPtr computeGeometry(VId vtx) const {return _painter->computeGeometry(vtx);}

  const  DressingFile* dressingFile() const {return _dressingFile;}

 private:

  const SymbLib* _symbLib;
  MTG* _mtg;
  Painter* _painter;
  const ColorLib* _colorLib;
  Plant* _plant;
  AmlBoolean _isInterpol;
  AmlBoolean _isMaxTreshold;
  AmlBoolean _isMinTreshold;

  FNode* _interpolFun;


  const DressingFile* _dressingFile;

};



#endif











