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
 *       $Id: dressingdata.cpp 3287 2007-06-08 11:27:37Z pradal $
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





#include "aml/ammodel.h"

#include "dressingdata.h"
#include "defaultval.h"

//#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"
#include "tool/util_math.h"

using namespace std;

DressingData::DressingData()
{
  cerr << "Creation of a Dressing Data" << endl;
  _symbol_path = DEFAULT_SYMBOL_PATH;
  _minLengthList=new LibList;
  _minTopDiaList=new LibList;
  _minBotDiaList=new LibList;
  _symbLib=new SymbLib;
  _colorLib=new ColorLib;
  _formsLib=new FormsLib;
  _diametersUnit=DEFAULT_DIAMETERS_UNIT;
  _lengthUnit=DEFAULT_LENGTH_UNIT;
  _defaultEdge=DEFAULT_EDGE;
  _defaultAlpha=DEFAULT_ALPHA;
  _defaultTeta=DEFAULT_TETA;
  _defaultPhi=DEFAULT_PHI;
  _defaultPsi=DEFAULT_PSI;
  _defaultCategory=DEFAULT_CATEGORY;
  _axeDefaultCategory=AXE_DEFAULT_CATEGORY;
  _isAlphaRelative=TRUE;
  _isIndice=FALSE;
  _phillotaxy=DEFAULT_AZIMUT;
  _mediumTresholdGreen=MEDIUM_TRESHOLD_GREEN;
  _mediumTresholdBlue=MEDIUM_TRESHOLD_BLUE;
  _mediumTresholdRed=MEDIUM_TRESHOLD_RED;
  _minTresholdGreen=MIN_TRESHOLD_GREEN;
  _minTresholdBlue=MIN_TRESHOLD_BLUE;
  _minTresholdRed=MIN_TRESHOLD_RED;
  _maxTresholdGreen=MAX_TRESHOLD_GREEN;
  _maxTresholdBlue=MAX_TRESHOLD_BLUE;
  _maxTresholdRed=MAX_TRESHOLD_RED;
  _deltaIndex=DELTA_INDEX;
  _elementLength=ELEMENT_LENGTH;
  _defaultDistance=DEFAULT_DISTANCE;
  _azimutUnit=DEFAULT_AZIMUTUNIT;
  _alphaUnit=DEFAULT_ALPHAUNIT;
  _tetaUnit=DEFAULT_TETAUNIT;
  _phiUnit=DEFAULT_PHIUNIT;
  _psiUnit=DEFAULT_PSIUNIT;
  _nbpLine=DEFAULT_NBPLINE;
  _fruitSymbol=DEFAULT_FRUIT_SYMBOL;
  _leafSymbol=DEFAULT_FRUIT_SYMBOL;
  _flowerSymbol=DEFAULT_FLOWER_SYMBOL;
  _verticille=DEFAULT_VERTICILLE;

  _defaultLeafTopDia=DEFAULT_LEAF_TOPDIA;
  _defaultLeafBottomDia=DEFAULT_LEAF_BOTTOMDIA;
  _defaultLeafLength=DEFAULT_LEAF_LENGTH;
  _defaultLeafAlpha=DEFAULT_LEAF_ALPHA;
  _defaultLeafBeta=DEFAULT_LEAF_BETA;

  _defaultFruitTopDia=DEFAULT_FRUIT_TOPDIA;
  _defaultFruitBottomDia=DEFAULT_FRUIT_BOTTOMDIA;
  _defaultFruitLength=DEFAULT_FRUIT_LENGTH;
  _defaultFruitAlpha=DEFAULT_FRUIT_ALPHA;
  _defaultFruitBeta=DEFAULT_FRUIT_BETA;

  _defaultFlowerTopDia=DEFAULT_FLOWER_TOPDIA;
  _defaultFlowerBottomDia=DEFAULT_FLOWER_BOTTOMDIA;
  _defaultFlowerLength=DEFAULT_FLOWER_LENGTH;
  _defaultFlowerAlpha=DEFAULT_FLOWER_ALPHA;
  _defaultFlowerBeta=DEFAULT_FLOWER_BETA;

}

DressingData::~DressingData()
{
  delete _minLengthList;
  _minLengthList = NULL;
  delete _minTopDiaList;
  delete _minBotDiaList;
  delete _symbLib;
  delete _colorLib;
  delete _formsLib;
}

ValType DressingData::getMinLength(char a_symb) const
{
  if(_minLengthList==NULL ||_minLengthList->empty())return DEFAULT_MIN_LENGTH;

  LibElement lb (a_symb);
  size_t index = RW_NPOS;
  
  if(_minLengthList!=NULL)
	index=_minLengthList->index(lb);
  ValType result=VAL_ERROR;

  if (index==RW_NPOS)
  {
    result=DEFAULT_MIN_LENGTH;
  }
  else
  {
    result=_minLengthList->at(index).getValue();
  }

  assert(result!=VAL_ERROR);

  return result;
}

ValType DressingData::getMinTopDia(char a_symb) const
{
  size_t index=_minTopDiaList->index(a_symb);
  ValType result=VAL_ERROR;

  if (index==RW_NPOS)
  {
    result=DEFAULT_MIN_TOPDIA;
  }
  else
  {
    result=_minTopDiaList->at(index).getValue();
  }

  assert(result!=VAL_ERROR);

  return result;
}

ValType DressingData::getMinBotDia(char a_symb) const
{
  size_t index=_minBotDiaList->index(a_symb);
  ValType result=VAL_ERROR;

  if (index==RW_NPOS)
  {
    result=DEFAULT_MIN_BOTDIA;
  }
  else
  {
    result=_minBotDiaList->at(index).getValue();
  }

  assert(result!=VAL_ERROR);

  return result;
}


Forms* DressingData::getBranchForm(IntType category) const
{
  return _formsLib->lookForAForm(category);
}


/*
ostream& DressingData::displayOneLine(ostream& o) const {

  o << "Dressing data file parsed." << endl;

    return o;

} */



void DressingData::report()
{
  cout << "Dressing file report " << endl;
  cout << "-------------------- " << endl << endl;

  cout << "Symbol path : " << _symbol_path << "." << endl;
  cout << "MinLength list" << endl;

  if (_minLengthList)
  {
    for(IntType i=0;i<_minLengthList->entries();i++)
    {
      cout << "Symbol : " << _minLengthList->at(i).getSymbol() << "   Value : ";
      cout << _minLengthList->at(i).getValue() << endl;
    }

    cout << endl;
  }
  else
  {
    cout << "Void. " << endl;
  }

  cout << "MinTopDiaList" << endl;
  cout << endl;

  if (_minTopDiaList)
  {
    for(IntType i=0;i<_minTopDiaList->entries();i++)
    {
      cout << "Symbol : " << _minTopDiaList->at(i).getSymbol() << "   Value : ";
      cout <<_minTopDiaList->at(i).getValue() << endl;
    }

    cout << endl;
  }
  else
  {
    cout << "Void. " << endl;
  }

  cout << "MinBotDiaList" << endl;
  cout << endl;

  if (_minBotDiaList)
  {
    for(IntType i=0;i<_minBotDiaList->entries();i++)
    {
      cout << "Symbol : " << _minBotDiaList->at(i).getSymbol() << "   Value : ";
      cout <<_minBotDiaList->at(i).getValue() << endl;
    }

    cout << endl;
  }
  else
  {
    cout << "Void. " << endl;
  }

  cout << endl;

  cout << "Length unit : " << _lengthUnit << endl;

  cout << "Diameters unit : " << _diametersUnit << endl;

  cout << "DefaultEdge : ";

  if (_defaultEdge==LESS)
  {
    cout << "LESS" << endl;
  }

  if (_defaultEdge==PLUS)
  {
    cout << "PLUS" << endl;
  }

  if (_defaultEdge==NONE)
  {
    cout << "NONE" << endl;
  }

  cout << "Default alpha : " << _defaultAlpha << endl;

  cout << "Default category : " << _defaultCategory << endl;

  cout << "Default axe category : " << _axeDefaultCategory << endl;

  cout << "Alpha is ";

  if (_isAlphaRelative)
  {
    cout << "Relative" << endl;
  }
  else
  {
    cout << "Absolute" << endl;
  }

  cout << "Phillotaxy : ";

  if (_isIndice)
  {
    cout << _nbTours << "/" << _nbLeaves << endl;
  }
  else
  {
    cout << _phillotaxy << endl;
  }

  cout << "MediumTresholdGreen : " << _mediumTresholdGreen << endl;
  cout << "MediumTresholdBlue  : " << _mediumTresholdBlue << endl;
  cout << "MediumTresholdRed   : " << _mediumTresholdRed << endl;
  cout << "MinTresholdGreen    : " << _minTresholdGreen << endl;
  cout << "MinTresholdBlue     : " << _minTresholdBlue << endl;
  cout << "MinTresholdRed      : " << _minTresholdRed << endl;
  cout << "MaxTresholdGreen    : " << _maxTresholdGreen << endl;
  cout << "MaxTresholdBlue     : " << _maxTresholdBlue << endl;
  cout << "MaxTresholdRed      : " << _maxTresholdRed << endl;
  cout << endl;
  cout << "Element length      : " << _elementLength << endl;
  cout << "Delta index         : " << _deltaIndex << endl;


  cout << "Symbols :" << endl;

  if (_symbLib)
  {
    const SymbolsTable st=_symbLib->getSymbolsTable();

    for (IntType i=0;i<st.entries();i++)
    {
      cout << "Symbol : " << st.at(i).getSymbol() << " File name : ";
      cout << st.at(i).getSymbolFileName() << " Symbol Name : " << st.at(i).getSymbolName();
      cout << endl;
    }
  }

  if (_formsLib)
  {
    _formsLib->report();
  }

}



