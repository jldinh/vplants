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
 *       $Id: dresser.cpp 3287 2007-06-08 11:27:37Z pradal $
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





#include <math.h>

#include "aml/ammodel.h"
#include "aml/array.h"

#include "dresser.h"

#include "plantframe.h"
#include "plant.h"
#include "dressingfile.h"
#include "linetree.h"

//#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"

//#include "GEOM/scne_smbtable.h"
#include "plantgl/scenegraph/core/smbtable.h"


#define  ERR_MSG_ARRAY          mtg_err_msgs_aml
#define  MODULE_NAME            "MTG"
extern const char *mtg_err_msgs_aml[];

using namespace std;

Dresser::Dresser(Plant& plant,
                 const DressingFile* dressing_file)
{
  _symbLib=&dressing_file->getSymbols();
  _mtg=plant.getMtg();
  _colorLib=&dressing_file->getColorsLib();
  _painter=new Painter(_mtg,&plant,this,*_colorLib,dressing_file);
  _plant=&plant;
  _isInterpol=FALSE;
  _isMaxTreshold=FALSE;
  _isMinTreshold=FALSE;

  _dressingFile=dressing_file;

 //_isMediumTreshold=FALSE;

/*
  IntType nb_branches=plant.nbBranches();

  for(IntType i=0;i<nb_branches;i++)
  {
    Branch* a_branch=plant._branches->at(i);
    BranchCompoList* components=a_branch->_components;

    IntType nb_compo=components->entries();

    for(IntType j=0;j<nb_compo;j++)
    {
      VId vertex=components->at(j).getVertex();
      _painter->insertElement(vertex);
    }
  }

*/

}

Dresser::~Dresser()
{
  delete _painter;
}

void Dresser::changeDressingFile(const DressingFile* dressing_file)
{
  _dressingFile=dressing_file;
  _symbLib=&dressing_file->getSymbols();
  _colorLib=&dressing_file->getColorsLib();
  _painter->changeDressingFile(dressing_file,_colorLib);
}


const ColorsTable& Dresser::getColorsTable() const
{
  return _painter->getColorsTable();
}

const CorrTable& Dresser::getCorrTable() const
{
  return _painter->getCorrTable();
}

const SymbLib& Dresser::getSymbLib() const
{
  return *_symbLib;
}


void Dresser::makeInterpol(FNode* function)
{
  _painter->setInterpolFunction(function);
  _isInterpol=TRUE;
  _interpolFun=function;
}

void Dresser::makeColorFun(FNode* function)
{
  _painter->setColorFunction(function);
}

void Dresser::makeColorRGBFun(FNode* function)
{
  _painter->setColorRGBFunction(function);
}

void Dresser::makeMaterialFun(FNode* function)
{
  _painter->setMaterialFunction(function);
}

void Dresser::makeGeometryFun(FNode* function)
{
  _painter->setGeometryFunction(function);
}


void Dresser::makeSymbolFun(FNode* symbol)
{
  _painter->setSymbolFunction(symbol);
}


void Dresser::makeMaxTreshold(ValType max)
{
  _painter->setMaxTreshold(max);
  _isMaxTreshold=TRUE;
}

void Dresser::makeMinTreshold(ValType min)
{
  _painter->setMinTreshold(min);
  _isMinTreshold=TRUE;
}

void Dresser::makeMedium(ValType medium)
{
  _painter->setMediumTreshold(medium);
}

void Dresser::dressThePlant(LineTree* lt)
{
  IntType nb_branches=_plant->nbBranches();


  if (lt->_areLeaves)
  {
    lt->_virtualLeaves->setEnvironement(lt, _dressingFile, _plant);
  }
  if (lt->_areFruits)
  {
    lt->_virtualFruits->setEnvironement(lt, _dressingFile, _plant);
  }

  if (lt->_areFlowers)
  {
    lt->_virtualFlowers->setEnvironement(lt, _dressingFile, _plant);
  }

  nb_branches=_plant->nbBranches();

  if (_isInterpol)
  {
    computeMinAndMax();
  }

  //IntType nb_branches=_plant->nbBranches();

  for(size_t i=0;i<nb_branches;i++)
  {
    Branch* a_branch=_plant->_branches->at(i);
    BranchCompoList* components=a_branch->_components;

    size_t nb_compo=components->entries();

    for(size_t j=0;j<nb_compo;j++)
    {
      VId vertex=components->at(j).getVertex();
      ValType range=1;

      if (_isInterpol)
      {
        range=_painter->fnodeValue(_interpolFun,vertex);
      }

      // This call make the computation of colors.
      _painter->insertElement(lt, vertex,range);

    }
  }

 // _painter->adjustColors();

}

void Dresser::computeMinAndMax()
{

  ValType mymin,mymax;

  if (_isInterpol)
  {
    size_t nb_branches=_plant->nbBranches();

    mymin=_painter->fnodeValue(_interpolFun,_plant->_branches->at(0)->_components->at(0).getVertex());
    mymax=_painter->fnodeValue(_interpolFun,_plant->_branches->at(0)->_components->at(0).getVertex());

    for(size_t i=0;i<nb_branches;i++)
    {
      Branch* a_branch=_plant->_branches->at(i);
      BranchCompoList* components=a_branch->_components;

      size_t nb_compo=components->entries();

      for(size_t j=0;j<nb_compo;j++)
      {
        VId vertex=components->at(j).getVertex();
        ValType value=_painter->fnodeValue(_interpolFun,vertex);

        if (mymax<value)
        {
          mymax=value;
        }
        if (mymin>value)
        {
          mymin=value;
        }
      }
    }

    if (!_isMaxTreshold)
    {
      _painter->setMaxTreshold(mymax);
    }
    if (!_isMinTreshold)
    {
      _painter->setMinTreshold(mymin);
    }
  }


}




Painter::Painter(MTG* mtg,
                 Plant* plant,
                  Dresser* dresser,
                 const ColorLib& colorlib,
                 const DressingFile* dressing_file)

{
  _dressingFile=dressing_file;
  _colorTable=new ColorsTable;
  _mtg=mtg;
  _plant=plant;
  _colorLib=&colorlib;
  _corrTable=new CorrTable;

  _isInterpol=FALSE;
  _isColor=FALSE;
  _isColorRGB=FALSE;
  _isSymbolFun=FALSE;
  _isMaxTreshold=FALSE;
  _isMinTreshold=FALSE;
  _isMediumTreshold=FALSE;

  _interpolFun=NULL;
  _geometryFun=NULL;
  _colorFun=NULL;
  _colorRGBFun=NULL;
  _materialFun=NULL;
  _symbolFun=NULL;
  _dresser=dresser;

}

Painter::~Painter()
{
  delete _colorTable;
  delete _corrTable;
}

void Painter::changeDressingFile(const DressingFile* dressing_file,const ColorLib* colorlib)
{
  _dressingFile=dressing_file;
  _colorLib=colorlib;
}


void Painter::insertElement(LineTree* lt, VId vertex,ValType range)
{

  // MODIFIER


  MyColor color;

  IntType last_vertex = _mtg->vertexNb()-1;

  if (vertex > last_vertex)
  {
    color=computeColorForVirtualVertex(lt, vertex);
  }
  else
  {
    color=computeColor(vertex);
  }


  if (!_colorTable->contains(color))
  {
    _colorTable->insert(color);
  }
  else
  {

    if (color.isInterpoled())
    {
      size_t index=_colorTable->index(color);

      if (color.getMin()<_colorTable->at(index).getMin())
      {
        _colorTable->at(index).putMin(color.getMin());

      }

      if (color.getMax()>_colorTable->at(index).getMax())
      {
        _colorTable->at(index).putMax(color.getMax());
      }
    }

  }

  SymbType n_symbol=(SymbType)_colorTable->index(color)+1;

  CorrElement corr_element(vertex,n_symbol,range);
  _corrTable->insert(corr_element);

}


void Painter::adjustColors()
{

  // Adjust the colors in case of interpolations.

  size_t n=_colorTable->entries();


  n=_corrTable->entries();


  if (_isInterpol)
  {
    size_t nb_element=_corrTable->entries();

    for (size_t i=0; i<nb_element;i++)
    {
      size_t symb=(size_t)_corrTable->at(i).getSymbol()-1;


      if (_colorTable->at(symb).isInterpoled())
      {
        // Case of interpolation : We must translate the range of the element
        // to have a min of zero.

        ValType delta=-_colorTable->at(symb).getMin();

        _corrTable->at(i).translateRange(delta);
      }
    }
  }

}


const ColorsTable& Painter::getColorsTable() const
{
  return *_colorTable;
}

const CorrTable& Painter::getCorrTable() const
{
  return *_corrTable;
}

ValType Painter::greenInterpol(ValType value)
{
  ValType result=VAL_ERROR;

  if (_maxTreshold==_minTreshold)
  {
    result=0;
  }
  else
  {
    if (!_isMediumTreshold)
    {

       result=(value-_minTreshold)/(_maxTreshold-_minTreshold);

    }
    else
    {
      if (value<_mediumTreshold)
      {
        result=(value-_minTreshold)/(_mediumTreshold-_minTreshold);

      }
      else
      {
        result=(value-_mediumTreshold)/(_maxTreshold-_mediumTreshold);

      }

      if (value==_mediumTreshold)
      {
        result=_dressingFile->getMediumTresholdGreen();
      }
    }

    if (value>_maxTreshold)
    {
      result=_dressingFile->getMaxTresholdGreen();
    }

    if (value<_minTreshold)
    {
      result=_dressingFile->getMinTresholdGreen();
    }
  }

  assert(result!=VAL_ERROR);

  return result;
}

ValType Painter::blueInterpol(ValType value)
{
  ValType result=0;

  if (_isMediumTreshold)
  {
    if (value<_mediumTreshold)
    {
      result=1;
    }

    if (value==_mediumTreshold)
    {
      result=_dressingFile->getMediumTresholdBlue();
    }
  }


  if (value>_maxTreshold)
  {
    result=_dressingFile->getMaxTresholdBlue();
  }

  if (value<_minTreshold)
  {
    result=_dressingFile->getMinTresholdBlue();
  }

  return result;
}

ValType Painter::redInterpol(ValType value)
{
  ValType result=1;

  if (_isMediumTreshold)
  {
    if (value>_mediumTreshold)
    {
      result=1;
    }

    if (value==_mediumTreshold)
    {
      result=_dressingFile->getMediumTresholdRed();
    }
  }

  if (value>_maxTreshold)
  {
    result=_dressingFile->getMaxTresholdRed();
  }

  if (value<_minTreshold)
  {
    result=_dressingFile->getMinTresholdRed();
  }

  return result;
}

AppearancePtr Painter::computeMaterial(VId vtx) const {

  FNode* matfun = _materialFun;
  AppearancePtr notfound(0);

  AppearanceSymbolTable* matsymbtable = _dressingFile->_mat_table;

  if (matfun && matsymbtable) {

    AMObjVector argobjs(1);
    argobjs[0] = AMObj(AMObjType::VTX, vtx);
    AMObj nameobj = (*_materialFun)(argobjs);

    if (nameobj.tag == AMObjType::STRING) {

      AMString ams = *(AMString*)nameobj.val.p;
      string matname(ams.data());

      AppearanceSymbolTable::iterator mst = matsymbtable->find(matname);

      if (mst != matsymbtable->end()) {
        // cerr << "MATERIAL : " << matname << " FOUND !!!!" << endl;
        return mst->second;
      }
      else  {
        // cerr << "MATERIAL : " << matname << " NOT FOUND !!!!" << endl;
        return notfound;
      }

    }
    else return notfound; // returns an invalid result

  }
  else return notfound;


}

GeometryPtr Painter::computeGeometry(VId vtx) const {

  FNode* geomfun = _geometryFun;
  GeometryPtr notfound;

  GeometrySymbolTable* geomsymbtable = _dressingFile->_geom_table;

  if (geomfun && geomsymbtable) {

    AMObjVector argobjs(1);
    argobjs[0] = AMObj(AMObjType::VTX, vtx);
    AMObj nameobj = (*_geometryFun)(argobjs);

    if (nameobj.tag == AMObjType::STRING) {

      AMString ams = *(AMString*)nameobj.val.p;
      string geomname(ams.data());

      GeometrySymbolTable::iterator mst = geomsymbtable->find(geomname);

      if (mst != geomsymbtable->end()) {
        // cerr << "GEOMETRY : " << geomname << " FOUND !!!!" << endl;
        return mst->second;
      }
      else  {
        // cerr << "GEOMETRY : " << geomname << " NOT FOUND !!!!" << endl;
        return notfound;
      }

    }
    else return notfound; // returns an invalid result

  }
  else return notfound;


}


// the correction seems to be done by the monitor
#if 0
#define  LINEAR_PERCEPTION
#endif

static ValType gamma_correction_red(ValType r) {

  return pow((double)r, 0.31);

}
static ValType gamma_correction_green(ValType r) {

  return pow((double)r, 0.61);

}
static ValType gamma_correction_blue(ValType r) {

  return pow((double)r, 0.08);

}


static void rgb_to_luv (ValType r, ValType g, ValType b,
                        ValType& l, ValType& u, ValType& v) {

#ifdef LINEAR_PERCEPTION

  l=gamma_correction_red(r);
  u=gamma_correction_green(g);
  v=gamma_correction_blue(b);


  /*
  if (g > 0.01) {

    l = (116.0 * exp((1/3.0) * log(g))) - 16.0 ;

  }
  else {
    l = 0.0;
  }

  ValType factor = (1/(r + 15.0 * g + 3.0 * b));
  ValType factor_w = (1/19.0);

  ValType u2 = 4.0 * r * factor;
  ValType v2 = 9.0 * g * factor;

  ValType u2_w = 4.0 * factor;
  ValType v2_w = 9.0 * factor;

  u = 13.0 * l *(u2-u2_w); // w for white
  v = 13.0 * l *(u2-u2_w);

  */

#else

  // make no change

  l=r;
  u=g;
  v=b;

#endif

}


MyColor Painter::computeColorForVirtualVertex(LineTree* lt, IntType virtual_vertex)
{


  VirtualSymbol v = lt->getVirtualSymbol(virtual_vertex);

  char a_symb=v._symbol;


  MyColor color = _colorLib->getColor(v._colorNumber);


  MyVector emission=color.emissionComponent();
  MyVector ambient=color.ambientComponent();
  MyVector diffuse=color.diffuseComponent();
  MyVector specular=color.specularComponent();
  ValType shininess=color.shininessComponent();

  MyColor result=MyColor (emission, ambient, diffuse, specular, shininess, a_symb );

  return result;
}

MyColor Painter::computeColor(VId vertex)
{

  char a_symb;

  if (!_isSymbolFun)
  {
    a_symb=_plant->symbol(vertex);
  }
  else
  {
    ValType tmp= fnodeValue(_symbolFun, vertex);

    if (tmp == LUNDEF)
    {
      a_symb=_plant->symbol(vertex);
    }
    else
    {
      a_symb= (char) tmp;
    }
  }

  MyColor result(a_symb);


  if (_isInterpol)
  {
    assert((_isMinTreshold) && (_isMaxTreshold));

    ValType value=fnodeValue(_interpolFun,vertex);

    // The interpolation is computed as a linear function of
    // the values of the vertices

    ValType green=greenInterpol(value);
    ValType blue=blueInterpol(value);
    ValType red=redInterpol(value);

    // Now, we transform this set of RGB values in order to obtain a
    // new set, in the so called LUV uniform color space (see Foley et al. 97, p584),
    // which gives a perceptually linear varition of colors.

    ValType l, u, v;

    rgb_to_luv(red, green, blue, l, u, v);


#ifdef LINEAR_PERCEPTION
    cerr << "RGB = (" << red << "," << green << "," << blue << ")" << endl;
    cerr << "LUV = (" << l << "," << u << "," << v << ")" << endl;
#endif

    MyVector component(l,u,v);
    //MyVector diffuse(1,1,1);

    result=MyColor (component, component, component, component, 1, a_symb);

  }
  else
  {
    if (_isColor)
    {
      IntType value=(IntType) fnodeValue(_colorFun,vertex);

      MyColor color=_colorLib->getColor(value);

      MyVector emission=color.emissionComponent();
      MyVector ambient=color.ambientComponent();
      MyVector diffuse=color.diffuseComponent();
      MyVector specular=color.specularComponent();
      ValType shininess=color.shininessComponent();

      result=MyColor (emission, ambient, diffuse, specular, shininess, a_symb );
    }
        else if (_isColorRGB){
                result = fnodeValueRGB(_colorRGBFun,vertex);
        }
  }

  return result;
}

/*
MyColor Painter::computeColor(VId vertex)
{

  char a_symb=_plant->symbol(vertex);
  MyColor result;

  if ((_isInterpol) || (_isColor))
  {
    if (_isColor)
    {
      IntType value=(IntType) fnodeValue(_colorFun,vertex);

      MyColor color=_colorLib->getColor(value);

      MyVector emission=color.emissionComponent();
      MyVector ambient=color.ambientComponent();
      MyVector diffuse=color.diffuseComponent();
      MyVector specular=color.specularComponent();
      ValType shininess=color.shininessComponent();

      result=MyColor (emission, ambient, diffuse, specular, shininess, a_symb );
    }
    else
    {
      result=MyColor (_colorLib->getColor(3)); // Red color
    }

    if (_isInterpol)
    {


      // assert((_isMinTreshold) && (_isMaxTreshold));

      ValType value=fnodeValue(_interpolFun,vertex);



      if (result.getMin()>value)
      {
        result.putMin(value);
      }
      if (result.getMax()<value)
      {
        result.putMax(value);
      }
    }
  }
  else
  {
    result= MyColor (a_symb);
  }

  return result;
} */


void Painter::setInterpolFunction(FNode* function)
{
  _interpolFun=function;

  if (function)
  {
    _isInterpol=TRUE;
  }
}

void Painter::setSymbolFunction(FNode* function)
{
  _symbolFun=function;

  if (function)
  {
    _isSymbolFun=TRUE;
  }
}

void Painter::setColorFunction(FNode* function)
{
  _colorFun=function;

  if (function)
  {
    _isColor=TRUE;
    _isColorRGB=FALSE;
  }
}

void Painter::setColorRGBFunction(FNode* function)
{
  _colorRGBFun=function;

  if (function)
  {
    _isColor=FALSE;
    _isColorRGB=TRUE;
  }
}

void Painter::setMaterialFunction(FNode* function)
{
  _materialFun=function;

  if (function)
  {
    _isMaterial=TRUE;
  }
}

void Painter::setGeometryFunction(FNode* function)
{
  _geometryFun=function;

  if (function)
  {
    _isGeometry=TRUE;
  }
}

void Painter::setMaxTreshold(ValType mmax)
{
  _maxTreshold=mmax;
  _isMaxTreshold=TRUE;
}

void Painter::setMinTreshold(ValType mmin)
{
  _minTreshold=mmin;
  _isMinTreshold=TRUE;
}

void Painter::setMediumTreshold(ValType medium)
{
  _mediumTreshold=medium;
  _isMediumTreshold=TRUE;
}

// Evaluate the FNode function function for a vertex

ValType Painter::fnodeValue(FNode* function,VId vertex)
{

  assert(function);

  ValType result=VAL_ERROR;

  AMObjVector argobjs(1); // Only one arg which is a vertex

  argobjs[0] = AMObj(AMObjType::VTX, vertex);

  AMObj result_obj = (*function)(argobjs);

  switch(result_obj.tag()) {

  case  AMObjType::INTEGER:
    result = (double) result_obj.val.i;
    break;
  case  AMObjType::REAL:
    result = result_obj.val.r;
    break;
 case  AMObjType::CHAR:
    result = (double) result_obj.val.c;
    break;

  default:
    //cerr << "Erreur !!" << endl;
    //cerr << "vtx  = " << vertex << endl;
    //cerr << "f(.) = " << result_obj << endl;
    result = (ValType) LUNDEF;
  }

  assert(result!=VAL_ERROR);

  return result;
}

MyColor Painter::fnodeValueRGB(FNode* function,VId vertex)
{

        assert(function);

        MyVector result(0.0,0.0,0.0);

        AMObjVector argobjs(1); // Only one arg which is an a vertex

        argobjs[0] = AMObj(AMObjType::VTX, vertex);

        AMObj result_obj = (*function)(argobjs);

        if(result_obj.tag() != AMObjType::ARRAY) return MyColor();
        const SLArray * mytuple = (const SLArray *)(result_obj.val.p);
        if(mytuple->entries() == 3) {

                for(int i = 0; i < 3; i++){
                        switch((*mytuple)[i].tag()) {

                        case  AMObjType::INTEGER:
                                result[i] = ((double) (*mytuple)[i].val.i)/255.0;
                                break;
                        case  AMObjType::REAL:
                                result[i] = (*mytuple)[i].val.r/255.0;
                                break;
                        case  AMObjType::CHAR:
                                result[i] = ((double) (*mytuple)[i].val.c)/255.0;
                                break;

                                //        default:
                                //cerr << "Erreur !!" << endl;
                                //cerr << "vtx  = " << vertex << endl;
                                //cerr << "f(.) = " << result_obj << endl;
                                //                result = (ValType) LUNDEF;
                        }
                }
        }
        else if(mytuple->entries() == 6
                   || mytuple->entries() == 9
                   || mytuple->entries() == 12
                   || mytuple->entries() == 13){
                MyVector ambient(0.071,0.050,0.011);
                MyVector diffuse(0.168,0.168,0.068);
                MyVector specular(0.168,0.168,0.068);
                MyVector emission(0.000,0.000,0.000);
                double shininess = 1.0;
                int i = 0;
                for(i = 0; i < 3; i++){
                        switch((*mytuple)[i].tag()) {
                        case  AMObjType::INTEGER:
                                ambient[i] = ((double) (*mytuple)[i].val.i)/255.0;
                                break;
                        case  AMObjType::REAL:
                                ambient[i] = (*mytuple)[i].val.r/255.0;
                                break;
                        case  AMObjType::CHAR:
                                ambient[i] = ((double) (*mytuple)[i].val.c)/255.0;
                                break;
                        }
                }
                for(i = 0; i < 3; i++){
                        switch((*mytuple)[i].tag()) {
                        case  AMObjType::INTEGER:
                                diffuse[i] = ((double) (*mytuple)[i+3].val.i)/255.0;
                                break;
                        case  AMObjType::REAL:
                                diffuse[i] = (*mytuple)[i+3].val.r/255.0;
                                break;
                        case  AMObjType::CHAR:
                                diffuse[i] = ((double) (*mytuple)[i+3].val.c)/255.0;
                                break;
                        }
                }
                if(mytuple->entries() >= 9){
                        for(i = 0; i < 3; i++){
                                switch((*mytuple)[i].tag()) {
                                case  AMObjType::INTEGER:
                                        specular[i] = ((double) (*mytuple)[i+6].val.i)/255.0;
                                        break;
                                case  AMObjType::REAL:
                                        specular[i] = (*mytuple)[i+6].val.r/255.0;
                                        break;
                                case  AMObjType::CHAR:
                                        specular[i] = ((double) (*mytuple)[i+6].val.c)/255.0;
                                        break;
                                }
                        }
                }
                if(mytuple->entries() >= 12){
                        for(i = 0; i < 3; i++){
                                switch((*mytuple)[i].tag()) {
                                case  AMObjType::INTEGER:
                                        emission[i] = ((double) (*mytuple)[i+9].val.i)/255.0;
                                        break;
                                case  AMObjType::REAL:
                                        emission[i] = (*mytuple)[i+9].val.r/255.0;
                                        break;
                                case  AMObjType::CHAR:
                                        emission[i] = ((double) (*mytuple)[i+9].val.c)/255.0;
                                        break;
                                }
                        }
                }
                if(mytuple->entries() == 13){
                                switch((*mytuple)[i].tag()) {
                                case  AMObjType::INTEGER:
                                        shininess = ((double) (*mytuple)[i+9].val.i)/255.0;
                                        break;
                                case  AMObjType::REAL:
                                        shininess = (*mytuple)[i+9].val.r/255.0;
                                        break;
                                case  AMObjType::CHAR:
                                        shininess = ((double) (*mytuple)[i+9].val.c)/255.0;
                                        break;
                                }
                }
                return MyColor(emission,ambient,diffuse,specular,shininess,UNDEF);
        }
        else return MyColor();
        // assert(result!=VAL_ERROR);

        return MyColor(result);
}

