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
 *       $Id: dressingfile.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _DRESSING_FILE_SAMIR_DEF_
#define _DRESSING_FILE_SAMIR_DEF_

#include "aml/ammodel.h"

#include <iostream>
#include "tool/rw_tokenizer.h"
#include "tool/rw_cstring.h"
#include "tool/rw_list.h"
//#include <rw/ctoken.h>
//#include <rw/rwfile.h>
//#include <rw/cstring.h>
//#include <rw/tvslist.h>
#include <fstream>
#include "definitions.h"
#include "vector.h"
#include "dressingdata.h"

#ifndef SYSTEM_IS__IRIX

#include "plantgl/pgl_geometry.h"
#include "plantgl/pgl_appearance.h"
PGL_USING_NAMESPACE

#endif

// Variables associees a un fichier

class FSymb
{
 public:

  FSymb(const FSymb&);
  FSymb(RWCString var_name,RWCString file_name);
  FSymb(RWCString var_name);

  AmlBoolean operator==(const FSymb& var_name) const;
  const FSymb& operator=(const FSymb&);

  RWCString _varName;
  RWCString _fileName;

};

typedef RWTValDlist<FSymb> VarTable;

// Noms associes a une forme de branche.

class NCrv
{
 public:

  NCrv(const NCrv&);
  NCrv(RWCString crv_name,ListOfMyVectors point_list);
  NCrv(RWCString crv_name);
  ~NCrv();

  AmlBoolean operator==(const NCrv&) const;
  const NCrv& operator=(const NCrv&);

  RWCString _crvName;
  ListOfMyVectors* _pointList;

};

typedef RWTValDlist<NCrv> CrvTable;


struct DRFErrorMsg {

  DRFErrorMsg(AmlBoolean, RWCString);
  DRFErrorMsg();

  AmlBoolean _isError;
  RWCString _errorMsg;

  void display();
};



// Objet interpreteur


class DressingFile : public DressingData
{
 public:

  DressingFile();
  DressingFile(const char* file_name);
  virtual ~DressingFile();

  RWCString* _displayMsg;
  std::string _filename;

  VarTable* _varTable;
  CrvTable* _crvTable;
  AmlBoolean _isValid;

  GeometrySymbolTable* _geom_table; // Symbol table containing Geoms (if any)
  AppearanceSymbolTable* _mat_table;  // Symbol table containing Materials (if any)

  virtual std::ostream& displayOneLine(std::ostream&) const;

  // Parse the file 'file_name'
  // Semantic functions

  DRFErrorMsg minLengthFun( RWCTokenizer next);
  DRFErrorMsg symbolFun( RWCTokenizer next);
  DRFErrorMsg geometryFun( RWCTokenizer next);
  DRFErrorMsg appearanceFun( RWCTokenizer next);
  DRFErrorMsg symbolPathFun( RWCTokenizer next);
  DRFErrorMsg symbolPatternFun( RWCTokenizer next);
  DRFErrorMsg branchPatternFun( RWCTokenizer next);
  DRFErrorMsg minTopDiaFun( RWCTokenizer next);
  DRFErrorMsg minBotDiaFun( RWCTokenizer next);
  DRFErrorMsg diametersUnitFun( RWCTokenizer next);
  DRFErrorMsg lengthUnitFun( RWCTokenizer next);
  DRFErrorMsg defaultEdgeFun( RWCTokenizer next);
  DRFErrorMsg defaultAlphaFun( RWCTokenizer next);
  DRFErrorMsg defaultTetaFun( RWCTokenizer next);
  DRFErrorMsg defaultPhiFun( RWCTokenizer next);
  DRFErrorMsg defaultPsiFun( RWCTokenizer next);
  DRFErrorMsg defaultCategoryFun( RWCTokenizer next);
  DRFErrorMsg defaultAxeCategoryFun( RWCTokenizer next);
  DRFErrorMsg phillotaxyFun( RWCTokenizer next);
  DRFErrorMsg formFun( RWCTokenizer next);
  DRFErrorMsg alphaFun( RWCTokenizer next);

  DRFErrorMsg mediumTresholdGreen(RWCTokenizer next);
  DRFErrorMsg maxTresholdGreen(RWCTokenizer next);
  DRFErrorMsg minTresholdGreen(RWCTokenizer next);

  DRFErrorMsg mediumTresholdBlue(RWCTokenizer next);
  DRFErrorMsg maxTresholdBlue(RWCTokenizer next);
  DRFErrorMsg minTresholdBlue(RWCTokenizer next);

  DRFErrorMsg mediumTresholdRed(RWCTokenizer next);
  DRFErrorMsg maxTresholdRed(RWCTokenizer next);
  DRFErrorMsg minTresholdRed(RWCTokenizer next);

  DRFErrorMsg deltaIndex(RWCTokenizer next);
  DRFErrorMsg elementLength(RWCTokenizer next);

  DRFErrorMsg azimutUnitFun(RWCTokenizer next);
  DRFErrorMsg alphaUnitFun(RWCTokenizer next);
  DRFErrorMsg defaultDistanceFun(RWCTokenizer next);
  DRFErrorMsg nbpLineFun(RWCTokenizer next);

  DRFErrorMsg verticilleFun(RWCTokenizer next);


  DRFErrorMsg leafSymbolFun(RWCTokenizer next);
  DRFErrorMsg leafTopDiaFun(RWCTokenizer next);
  DRFErrorMsg leafBottomDiaFun(RWCTokenizer next);
  DRFErrorMsg leafLengthFun(RWCTokenizer next);
  DRFErrorMsg leafAlphaFun(RWCTokenizer next);
  DRFErrorMsg leafBetaFun(RWCTokenizer next);

  DRFErrorMsg fruitSymbolFun(RWCTokenizer next);
  DRFErrorMsg fruitTopDiaFun(RWCTokenizer next);
  DRFErrorMsg fruitBottomDiaFun(RWCTokenizer next);
  DRFErrorMsg fruitLengthFun(RWCTokenizer next);
  DRFErrorMsg fruitAlphaFun(RWCTokenizer next);
  DRFErrorMsg fruitBetaFun(RWCTokenizer next);

  DRFErrorMsg flowerSymbolFun(RWCTokenizer next);
  DRFErrorMsg flowerTopDiaFun(RWCTokenizer next);
  DRFErrorMsg flowerBottomDiaFun(RWCTokenizer next);
  DRFErrorMsg flowerLengthFun(RWCTokenizer next);
  DRFErrorMsg flowerAlphaFun(RWCTokenizer next);
  DRFErrorMsg flowerBetaFun(RWCTokenizer next);




 //  AmlBoolean function(const char* chaine);

  // Tools functions

  AmlBoolean readCrvFile(const char* file_name);

};


#endif














