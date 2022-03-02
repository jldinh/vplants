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
 *       $Id: dressingdata.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _DRESSING_DATA_SAMIR_DEF_
#define _DRESSING_DATA_SAMIR_DEF_

#include "aml/ammodel.h"
#include "definitions.h"
#include "symbol.h"
#include "color.h"
#include "forms.h"
#include "liblist.h"

class DressingData : public AMModel
{
 public:

  // Constructors

  DressingData();
  virtual ~DressingData();

  virtual std::ostream& displayOneLine(std::ostream&) const=0;

  const SymbLib& getSymbols() const {return *_symbLib;};
  const ColorLib& getColorsLib() const {return *_colorLib;};

  Forms* getBranchForm(IntType category) const;

  ValType getMinLength(char) const;
  ValType getMinTopDia(char) const;
  ValType getMinBotDia(char) const;
  ValType getLengthUnit() const {return _lengthUnit;};
  ValType getDiametersUnit() const {return _diametersUnit;};
  EType getDefaultEdge() const {return _defaultEdge;};
  ValType getDefaultAlpha() const {return _defaultAlpha;};
  ValType getDefaultTeta() const {return _defaultTeta;};
  ValType getDefaultPhi() const {return _defaultPhi;};
  ValType getDefaultPsi() const {return _defaultPsi;};
  IntType getDefaultCategory() const {return _defaultCategory;};
  IntType getAxeDefaultCategory() const {return _axeDefaultCategory;};
  AmlBoolean isIndicePhillotaxy() const {return _isIndice;};
  ValType getPhillotaxy() const {return _phillotaxy;};
  ValType getNbTours() const {return _nbTours;};
  ValType getNbLeaves() const {return _nbLeaves;};
  AmlBoolean isAlphaRelative() const {return _isAlphaRelative;};

  ValType getMediumTresholdGreen() const {return _mediumTresholdGreen;};
  ValType getMaxTresholdGreen() const {return _maxTresholdGreen;};
  ValType getMinTresholdGreen() const {return _minTresholdGreen;};

  ValType getMediumTresholdBlue() const {return _mediumTresholdBlue;};
  ValType getMaxTresholdBlue() const {return _maxTresholdBlue;};
  ValType getMinTresholdBlue() const {return _minTresholdBlue;};

  ValType getMediumTresholdRed() const {return _mediumTresholdRed;};
  ValType getMaxTresholdRed() const {return _maxTresholdRed;};
  ValType getMinTresholdRed() const {return _minTresholdRed;};

  ValType getDeltaIndex() const {return _deltaIndex;};
  ValType getElementLength() const {return _elementLength;};

  ValType getDefaultDistance() const { return _defaultDistance;};
  ValType getNbPlantsPerLine() const { return _nbpLine;};
  ValType getAzimutUnit() const { return _azimutUnit;};
  ValType getAlphaUnit() const { return _alphaUnit;};
  ValType getTetaUnit() const { return _tetaUnit;};
  ValType getPhiUnit() const { return _phiUnit;};
  ValType getPsiUnit() const { return _psiUnit;};

  IntType getDefaultVerticille() const { return _verticille; };

  ValType getDefaultLeafLength() const { return _defaultLeafLength; };
  ValType getDefaultLeafBottomDia() const { return _defaultLeafBottomDia; };
  ValType getDefaultLeafTopDia() const { return _defaultLeafTopDia; };
  ValType getDefaultLeafAlpha() const { return _defaultLeafAlpha; };
  ValType getDefaultLeafBeta() const { return _defaultLeafBeta; };

  ValType getDefaultFruitLength() const { return _defaultFruitLength; };
  ValType getDefaultFruitBottomDia() const { return _defaultFruitBottomDia; };
  ValType getDefaultFruitTopDia() const { return _defaultFruitTopDia; };
  ValType getDefaultFruitAlpha() const { return _defaultFruitAlpha; };
  ValType getDefaultFruitBeta() const { return _defaultFruitBeta; };

  ValType getDefaultFlowerLength() const { return _defaultFlowerLength; };
  ValType getDefaultFlowerBottomDia() const { return _defaultFlowerBottomDia; };
  ValType getDefaultFlowerTopDia() const { return _defaultFlowerTopDia; };
  ValType getDefaultFlowerAlpha() const { return _defaultFlowerAlpha; };
  ValType getDefaultFlowerBeta() const { return _defaultFlowerBeta; };


  // Default symbols

  char getLeafSymbol() const { return _leafSymbol; };
  char getFruitSymbol()  const { return _fruitSymbol; };
  char getFlowerSymbol() const { return _flowerSymbol; };

  const char* symbolPath() const {return _symbol_path.data();}

  // For debugging

  void report();

 protected:

  RWCString _symbol_path;

  LibList* _minLengthList;
  LibList* _minTopDiaList;
  LibList* _minBotDiaList;
  ValType _lengthUnit;
  ValType _diametersUnit;
  SymbLib* _symbLib;
  ColorLib* _colorLib;
  EType _defaultEdge;
  AmlBoolean _isAlphaRelative;
  ValType _defaultAlpha;
  ValType _defaultTeta;
  ValType _defaultPhi;
  ValType _defaultPsi;
  FormsLib* _formsLib;
  IntType _defaultCategory;
  IntType _axeDefaultCategory;
  ValType _phillotaxy;
  ValType _nbTours;
  ValType _nbLeaves;
  AmlBoolean _isIndice;
  ValType _mediumTresholdGreen;
  ValType _minTresholdGreen;
  ValType _maxTresholdGreen;
  ValType _mediumTresholdBlue;
  ValType _minTresholdBlue;
  ValType _maxTresholdBlue;
  ValType _mediumTresholdRed;
  ValType _minTresholdRed;
  ValType _maxTresholdRed;
  ValType _elementLength;
  IntType _deltaIndex;
  ValType _defaultDistance;
  ValType _nbpLine;
  ValType _azimutUnit;
  ValType _alphaUnit;
  ValType _tetaUnit;
  ValType _phiUnit;
  ValType _psiUnit;
  IntType _verticille;


  ValType _defaultLeafBottomDia;
  ValType _defaultLeafTopDia;
  ValType _defaultLeafLength;
  ValType _defaultLeafAlpha;
  ValType _defaultLeafBeta;

  ValType _defaultFruitBottomDia;
  ValType _defaultFruitTopDia;
  ValType _defaultFruitLength;
  ValType _defaultFruitAlpha;
  ValType _defaultFruitBeta;

  ValType _defaultFlowerBottomDia;
  ValType _defaultFlowerTopDia;
  ValType _defaultFlowerLength;
  ValType _defaultFlowerAlpha;
  ValType _defaultFlowerBeta;

  char _fruitSymbol;
  char _flowerSymbol;
  char _leafSymbol;

};

#endif






