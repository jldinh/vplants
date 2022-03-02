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
 *       $Id: dressingfile.cpp 17611 2014-10-17 13:20:41Z pradal $
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




#include "plantgl/tool/dirnames.h"
TOOLS_USING_NAMESPACE

//#include "GEOM/scne_smbtable.h"
#include "plantgl/scenegraph/core/smbtable.h"
#include "plantgl/algo/codec/cdc_geom.h"

#include "aml/ammodel.h"

#include "dressingfile.h"
#include <stdlib.h>
#include "forms.h"
#include "symbol.h"

#include "sam_msg.h"

using namespace std;

// If we want to add a command to the DressingFile syntax
// we must do it here.

typedef DRFErrorMsg (DressingFile::*actfun) ( RWCTokenizer );


struct DressingFileTable
{
  DressingFileTable(RWCString cc ,actfun ff){
    command=cc;
    function=ff;
  }

  DressingFileTable()
  {
    command=RWCString();
    function=NULL;
  }

  RWCString command;
  actfun function;

};

 // Number of instructions accepted by the DressingFile.

#define NB_INST 55


DressingFileTable _pTable[]={ DressingFileTable (RWCString ("MinLength"),
                                                        &DressingFile::minLengthFun),
                                     DressingFileTable (RWCString ("Class"),
                                                        &DressingFile::symbolFun),
                                     DressingFileTable (RWCString ("Geometry"),
                                                        &DressingFile::geometryFun),
                                     DressingFileTable (RWCString ("Appearance"),
                                                        &DressingFile::appearanceFun),
                                     DressingFileTable (RWCString ("SMBPath"),
                                                        &DressingFile::symbolPathFun),
                                     DressingFileTable (RWCString ("SMBModel"),
                                                        &DressingFile::symbolPatternFun),
                                     DressingFileTable (RWCString ("BranchPattern"),
                                                        &DressingFile:: branchPatternFun),
                                     DressingFileTable (RWCString ("MinTopDiameter"),
                                                        &DressingFile::minTopDiaFun),
                                     DressingFileTable (RWCString ("MinBottomDiameter"),
                                                        &DressingFile::minBotDiaFun),
                                     DressingFileTable (RWCString ("DiameterUnit"),
                                                        &DressingFile::diametersUnitFun),
                                     DressingFileTable (RWCString ("LengthUnit"),
                                                        &DressingFile::lengthUnitFun),
                                     DressingFileTable (RWCString ("DefaultEdge"),
                                                        &DressingFile::defaultEdgeFun),
                                     DressingFileTable (RWCString ("DefaultAlpha"),
                                                        &DressingFile::defaultAlphaFun),
                                     DressingFileTable (RWCString ("DefaultTeta"),
                                                        &DressingFile::defaultTetaFun),
                                     DressingFileTable (RWCString ("DefaultPhi"),
                                                        &DressingFile::defaultPhiFun),
                                     DressingFileTable (RWCString ("DefaultPsi"),
                                                        &DressingFile::defaultPsiFun),
                                     DressingFileTable (RWCString ("DefaultCategory"),
                                                        &DressingFile::defaultCategoryFun),
                                     DressingFileTable (RWCString ("DefaultTrunkCategory"),
                                                        &DressingFile::defaultAxeCategoryFun),
                                     DressingFileTable (RWCString ("Phyllotaxy"),
                                                        &DressingFile::phillotaxyFun),
                                     DressingFileTable (RWCString ("Form"),
                                                        &DressingFile::formFun),
                                     DressingFileTable (RWCString ("Alpha"),
                                                        &DressingFile::alphaFun),
                                     DressingFileTable (RWCString ("MediumThresholdGreen"),
                                                        &DressingFile::mediumTresholdGreen),
                                     DressingFileTable (RWCString ("MediumThresholdBlue"),
                                                        &DressingFile::mediumTresholdBlue),
                                     DressingFileTable (RWCString ("MediumThresholdRed"),
                                                        &DressingFile::mediumTresholdRed),
                                     DressingFileTable (RWCString ("MinThresholdGreen"),
                                                        &DressingFile::minTresholdGreen),
                                     DressingFileTable (RWCString ("MinThresholdBlue"),
                                                        &DressingFile::minTresholdBlue),
                                     DressingFileTable (RWCString ("MinThresholdRed"),
                                                        &DressingFile::minTresholdRed),
                                     DressingFileTable (RWCString ("MaxThresholdGreen"),
                                                        &DressingFile::maxTresholdGreen),
                                     DressingFileTable (RWCString ("MaxThresholdBlue"),
                                                        &DressingFile::maxTresholdBlue),
                                     DressingFileTable (RWCString ("MaxThresholdRed"),
                                                        &DressingFile::maxTresholdRed),
                                     DressingFileTable (RWCString ("DeltaIndex"),
                                                        &DressingFile::deltaIndex),
                                     DressingFileTable (RWCString ("ElementLength"),
                                                        &DressingFile::elementLength),
                                     DressingFileTable (RWCString ("AzimuthUnit"),
                                                        &DressingFile::azimutUnitFun),
                                     DressingFileTable (RWCString ("AlphaUnit"),
                                                        &DressingFile::alphaUnitFun),
                                     DressingFileTable (RWCString ("DefaultDistance"),
                                                        &DressingFile::defaultDistanceFun),
                                     DressingFileTable (RWCString ("NbPlantsPerLine"),
                                                        &DressingFile::nbpLineFun),
                                     DressingFileTable (RWCString ("FruitClass"),
                                                        &DressingFile::fruitSymbolFun),
                                     DressingFileTable (RWCString ("LeafClass"),
                                                        &DressingFile::leafSymbolFun),
                                     DressingFileTable (RWCString ("FlowerClass"),
                                                        &DressingFile::flowerSymbolFun),
                                     DressingFileTable (RWCString ("Whorl"),
                                                        &DressingFile::verticilleFun),

                                     DressingFileTable (RWCString ("LeafLength"),
                                                        &DressingFile::leafLengthFun),
                                     DressingFileTable (RWCString ("LeafTopDiameter"),
                                                        &DressingFile::leafTopDiaFun),
                                     DressingFileTable (RWCString ("LeafBottomDiameter"),
                                                        &DressingFile::leafBottomDiaFun),
                                     DressingFileTable (RWCString ("LeafAlpha"),
                                                        &DressingFile::leafAlphaFun),
                                     DressingFileTable (RWCString ("LeafBeta"),
                                                        &DressingFile::leafBetaFun),


                                     DressingFileTable (RWCString ("FruitLength"),
                                                        &DressingFile::fruitLengthFun),
                                     DressingFileTable (RWCString ("FruitTopDiameter"),
                                                        &DressingFile::fruitTopDiaFun),
                                     DressingFileTable (RWCString ("FruitBottomDiameter"),
                                                        &DressingFile::fruitBottomDiaFun),
                                     DressingFileTable (RWCString ("FruitAlpha"),
                                                        &DressingFile::fruitAlphaFun),
                                     DressingFileTable (RWCString ("FruitBeta"),
                                                        &DressingFile::fruitBetaFun),

                                     DressingFileTable (RWCString ("FlowerLength"),
                                                        &DressingFile::flowerLengthFun),
                                     DressingFileTable (RWCString ("FlowerTopDiameter"),
                                                        &DressingFile::flowerTopDiaFun),
                                     DressingFileTable (RWCString ("FlowerBottomDiameter"),
                                                        &DressingFile::flowerBottomDiaFun),
                                     DressingFileTable (RWCString ("FlowerAlpha"),
                                                        &DressingFile::flowerAlphaFun),
                                     DressingFileTable (RWCString ("FlowerBeta"),
                                                        &DressingFile::flowerBetaFun)


                                   };



/****************************************************/
/*                                                  */
/*                 Table des erreurs                */
/*                                                  */
/****************************************************/


// #define NB_ERR_MSG 13

const RWCString ERRORS_MSG[] = { RWCString(" No message."),
                                           RWCString(" `=' expected."),
                                           RWCString(" Right value expected."),
                                           RWCString(" Unknown value."),
                                           RWCString(" Bad number of parameters."),
                                           RWCString(" Undefined form."),
                                           RWCString(" `=' expected."),
                                           RWCString(" Undefined symbol "),
                                           RWCString(" Alias already used."),
                                           RWCString(" Error in reading curve file."),
                                           RWCString(" Error in reading color file."),
                                           RWCString(" Curve file name expected."),
                                           RWCString("' was already associated with a pattern.")
                                         };



/*****************************************************/
/*          Interpreteur des DressingFiles           */
/*****************************************************/



FSymb::FSymb(RWCString var_name,
             RWCString file_name)
{
  _varName=var_name;
  _fileName=file_name;
}

FSymb::FSymb(const FSymb& fsymb)
{
  _varName=fsymb._varName;
  _fileName=fsymb._fileName;
}

FSymb::FSymb(RWCString var_name)
{
  _varName=var_name;
}

AmlBoolean FSymb::operator==(const FSymb& fsymb) const
{
  if (_varName==fsymb._varName)
  {
    return TRUE;
  }
  else
  {
    return FALSE;
  }
}

const FSymb& FSymb::operator=(const FSymb& fsymb)
{
  if (this!=&fsymb)
  {
    _varName=fsymb._varName;
    _fileName=fsymb._fileName;

  }
  return *this;
}

/************************************************************/
/*             Table des formes de branches                 */
/************************************************************/


NCrv::NCrv(RWCString name,
           ListOfMyVectors point_list)
{
  _crvName=name;
  _pointList=new ListOfMyVectors (point_list);
}

NCrv::NCrv(const NCrv& ncrv)
{
  _crvName=ncrv._crvName;
  _pointList=new ListOfMyVectors (*ncrv._pointList);
}

NCrv::NCrv(RWCString name)
{
  _crvName=name;
  _pointList=new ListOfMyVectors;
}


NCrv::~NCrv()
{
  delete _pointList;
}

AmlBoolean NCrv::operator==(const NCrv& ncrv) const
{
  if (_crvName==ncrv._crvName)
  {
    return TRUE;
  }
  else
  {
    return FALSE;
  }
}

const NCrv& NCrv::operator=(const NCrv& ncrv)
{
  if (this!=&ncrv)
  {
    delete _pointList;

    _crvName=ncrv._crvName;
    _pointList=new ListOfMyVectors (*ncrv._pointList);
  }

  return *this;
}

/***************************************************/
/*           Methodes pour les erreurs             */
/***************************************************/

DRFErrorMsg::DRFErrorMsg(AmlBoolean is_error,
                         RWCString str_msg)
{
  _errorMsg= str_msg;
  _isError=is_error;
}

DRFErrorMsg::DRFErrorMsg()
{
  _isError=FALSE;
}

void DRFErrorMsg::display()
{
  cout << _errorMsg.data() << endl;
}

/***************************************************/
/*            Methodes du DressingFile             */
/***************************************************/


DressingFile::DressingFile() : DressingData()
{
  _isValid=FALSE;
    _geom_table = 0; // this will be initialized only if Geom objects are loaded
    _mat_table = 0; // this will be initialized only if Geom objects are loaded
  _displayMsg=new RWCString(APPL_MSG[DEFAULT_DRD_MSG]);
}

DressingFile::DressingFile(const char* file_name) : DressingData(), _filename(file_name)
{
  // On vide les listes

  ifstream file(file_name);

  _isValid=TRUE;

  if (!!file)
  {

    _displayMsg=new RWCString (APPL_MSG[DRD_FILE_MSG]);
    *_displayMsg+=RWCString(file_name)+RWCString("'.");

    _symbLib->clear();
    _formsLib->clear();

    _varTable=new VarTable;
    _crvTable=new CrvTable;

    _geom_table = 0; // this will be initialized only if Geom objects are loaded
    _mat_table = 0; // this will be initialized only if Geom objects are loaded

    RWCString chaine;

    int i=0;
    string cwd = get_cwd();

    if (cwd == "") { // stores the current cwd
      _isValid=FALSE;
    }
    // else cerr << "cwd:             [" << cwd_path << "]" << endl;

    // get the directory part of a filename (the filename might be not expanded)
    // the filename stored in the DressingFile object might be "../../fruit.drf"
    // or simply fruit.drf for example.

    string new_cwd = get_dirname(_filename);
    // cerr << "changing cwd: cd [" << new_cwd << "]" << endl;

    if (!chg_dir(new_cwd)) { // the name of the current file becomes the cwd
      _isValid=FALSE;
    }

    while(chaine.readLine(file,FALSE))
    {
      i++;
      size_t pos=chaine.first('#');

      if (pos!=RW_NPOS)
      {
        // Enlever les commentaires de la ligne
        chaine.remove(pos);
      }
      if (!chaine.isNull())
      {
        RWCTokenizer next(chaine);

        RWCString token;

        RWBoolean found=FALSE;

        while((!(token=next()).isNull()) && (!found))
        {
          int j=0;

          while ((!found) && (j<NB_INST))
          {
            if (_pTable[j].command==token)
            {
              actfun f=_pTable[j].function;

              DRFErrorMsg drf_er_msg = (this->*f) (next);

              if (drf_er_msg._isError)
              {
                cerr << "Dressing data file parser : Error at line " << i << " : ";
                drf_er_msg.display();
                _isValid=FALSE;
              }

              found=TRUE;

            }
            j++;
          }
          if (!found)
          {
            found=TRUE;
            cerr << "Dressing data file parser : Syntax error at line " << i << " . " << endl;
            _isValid=FALSE;
          }
        }
      }
    } // end of while(chaine.readLine(file,FALSE))

    // cerr << "restoring original cwd ..." << endl;

    if (!chg_dir(cwd)) {  // restores the current file becomes the cwd
      _isValid=FALSE;
    }

  }
  else
  {
    _displayMsg=new RWCString (APPL_MSG[DRD_ERR_MSG]);
    *_displayMsg+=RWCString(file_name)+RWCString("'.");
    _isValid=FALSE;
  }

  // report();
}

DressingFile::~DressingFile()
{
  if (_isValid)
  {
    delete _varTable;
    delete _crvTable;
  }
  delete _displayMsg;
}


DRFErrorMsg  DressingFile::minLengthFun( RWCTokenizer next)
{
  RWCString* error_msg=NULL;
  AmlBoolean is_error=FALSE;

  ValType value;
  char symbol;

  RWCString token;

  if (!(token=next()).isNull())
  {
    symbol=*token.data();
    if (!(token=next()).isNull())
    {
      if (token!="=")
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[1]);
      }
      else
      {
        if (!(token=next()).isNull())
        {
          value=atof(token.data());
        }
        else
        {
          is_error=TRUE;
          error_msg=new RWCString (ERRORS_MSG[2]);
        }
      }
    }
  }

  if (!is_error)
  {
    LibElement lb (symbol,value);
    _minLengthList->insert(lb);
  }


  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }
}


DRFErrorMsg DressingFile::symbolFun( RWCTokenizer next)
{

  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;
  char symbol;
  RWCString file_name;
  RWCString* var_name=NULL;

  if (!(token=next()).isNull())
  {
    symbol=*token.data();

    if (!(token=next()).isNull())
    {
      if (token!="=")
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[1]);
      }
      else
      {
        if (!(token=next()).isNull())
        {
          var_name=new RWCString (token.data());
          size_t index=_varTable->index(FSymb(*var_name));

          // cerr << "reading dressing file: " << " looking for geom model labelled : " << *var_name << endl;
          if (index!=RW_NPOS)
          {
            file_name= RWCString(_varTable->at(index)._fileName);
      if( !exists(set_suffix(cat_dir_file(_symbol_path,file_name),"smb")))
        {
        is_error=true;
        error_msg=new RWCString(ERRORS_MSG[7]);
        *error_msg+=RWCString(set_suffix(cat_dir_file(_symbol_path,file_name),"smb"));
        }
          }
          else
          {
            GeometrySymbolTable* pst = _geom_table;

            if (pst) {  // a set of geom objects has been declared in the dressing file: Geometry = "file"

              cerr << "Class " << symbol << ": looking for geom model labelled " << var_name->data() << " in GeomTable: " << flush;
              GeometrySymbolTable::iterator _i = pst->find(var_name->data());

              if (_i != pst->end()) {   // if the symbol is in the table, get it
                cerr << " found." << endl;
                // psymbol = _i->second; // nothing to do
              }
              else { // Not found
                cerr << " not found." << endl;
                is_error=TRUE;
                error_msg=new RWCString (ERRORS_MSG[7]);
                *error_msg+=RWCString("`")+RWCString(*var_name)+RWCString("'.");
              }

            }
            else {
              cerr << "No Geom table" << endl;
              is_error=TRUE;
              error_msg=new RWCString (ERRORS_MSG[7]);
              *error_msg+=RWCString("`")+RWCString(*var_name)+RWCString("'.");
            }

          }
        }
        else
        {
          is_error=TRUE;
          error_msg=new RWCString(ERRORS_MSG[4]);
        }
      }
    }
    else
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[4]);
    }
  }
  else
  {
    is_error=TRUE;
    error_msg=new RWCString(ERRORS_MSG[4]);
  }

  if (!is_error)
  {

    MySymbol s (file_name.data(),
                var_name->data(),
                symbol);

    if (!_symbLib->addSymbol(s))
    {
      error_msg=new RWCString("Symbol `");
      *error_msg+=RWCString(symbol)+RWCString(ERRORS_MSG[12]);
    }
  }

  if (var_name)
  {
    delete var_name;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg DressingFile::symbolPathFun( RWCTokenizer next)
{

  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
    {
    if (token!="=")
      {
            is_error=TRUE;
            error_msg=new RWCString (ERRORS_MSG[1]);
            }
    else
            {
            if (!(token=next("\t\n")).isNull())
              {

              // computes an expanded path where .././ forms have been interpreted
              _symbol_path = absolute_filename(short_dirname(token.data())).c_str();


              if ((_symbol_path.length() == 0) || (!exists(_symbol_path)) )
          {
                      is_error=TRUE;
                      error_msg=new RWCString(ERRORS_MSG[4]);
                }
            }
          else
            {
              is_error=TRUE;
              error_msg=new RWCString(ERRORS_MSG[4]);
            }
        }
    }
  else
  {
    is_error=TRUE;
    error_msg=new RWCString(ERRORS_MSG[4]);
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg DressingFile::geometryFun( RWCTokenizer next)
{

  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
    {
      if (token!="=")
        {
          is_error=TRUE;
          error_msg=new RWCString (ERRORS_MSG[1]);
        }
      else
        {
          if (!(token=next()).isNull())
            {

              // computes an expanded path where .././ forms have been interpreted
              string filename = absolute_filename(token.data()).c_str();

              if (filename.length() == 0) {
              }

              cerr << "Loading Geometric objects from file : " << filename << " ... " << endl;


              SceneObjectSymbolTable * _table = new SceneObjectSymbolTable;
	      #ifdef WITH_OLD_GEOM
              bool parse_ok=SceneObject::parse(filename.c_str(), cerr, *_table);
              #else
	      std::ifstream _file(filename.c_str());
	      ScenePtr scene;
	      bool parse_ok = geom_read(_file, *_table, scene, filename);
	      #endif

              if (!parse_ok) {
                delete _table;
                is_error=TRUE;
                error_msg=new RWCString(ERRORS_MSG[4]);
              }
              else {

                for (SceneObjectSymbolTable::iterator sti = _table->begin();
                     sti != _table->end();
                     sti++) {
                    GeometryPtr _geom = dynamic_pointer_cast<Geometry>(sti->second);
                    if( _geom ){
                        if (!_geom_table) _geom_table = new GeometrySymbolTable;
                        else{
                            GeometrySymbolTable::iterator _it = _geom_table->find( sti->first );
                            if(_it!=_geom_table->end())
                                cerr << "Warning ! Multiple Definition of '" << sti->first.c_str() << "'. Overloading." << endl;
                        }
                        (*_geom_table)[sti->first]=_geom;
                        cerr << "Adding symbol '" << sti->first.c_str() << "'." << endl;
                    }
                    else{
                        AppearancePtr _app = dynamic_pointer_cast<Appearance>(sti->second);
                        if( _app ){
                            if (!_mat_table) _mat_table = new AppearanceSymbolTable;
                            else{
                                AppearanceSymbolTable::iterator _it = _mat_table->find( sti->first );
                                if(_it!=_mat_table->end())
                                    cerr << "Warning ! Multiple Definition of '" << sti->first.c_str() << "'. Overloading." << endl;
                            }
                            (*_mat_table)[sti->first]=AppearancePtr(_app);
                        }
                    }
                }


                cerr << "Done. " << endl;
                /*
                cerr << "List of object loaded : " << endl;

                Printer pp(cerr,cerr);

                for (GeometrySymbolTable::iterator sti = _geom_table->begin();
                     sti != _geom_table->end();
                     sti++) {
                  cerr << sti->first << " = ";
                  sti->second->apply(pp);
                  cerr << endl;
                }
                */
              }

            }
          else
            {
              is_error=TRUE;
              error_msg=new RWCString(ERRORS_MSG[4]);
            }
        }
    }
  else
  {
    is_error=TRUE;
    error_msg=new RWCString(ERRORS_MSG[4]);
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg DressingFile::appearanceFun( RWCTokenizer next)
{

  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
    {
      if (token!="=")
        {
          is_error=TRUE;
          error_msg=new RWCString (ERRORS_MSG[1]);
        }
      else
        {
          if (!(token=next()).isNull())
            {

              // computes an expanded path where .././ forms have been interpreted
              string filename = absolute_filename(token.data()).c_str();

              if (filename.length() == 0) {
              }

              cerr << "Loading Appearance objects from file : " << filename << " ... " << endl;

              //if (!_mat_table) _mat_table = new AppearanceSymbolTable;


              SceneObjectSymbolTable * _table = new SceneObjectSymbolTable;
              
              #ifdef WITH_OLD_GEOM
              bool parse_ok=SceneObject::parse(filename.c_str(), cerr, *_table);
              #else
	      std::ifstream _file(filename.c_str());
	      ScenePtr scene;
	      bool parse_ok = geom_read(_file, *_table, scene, filename);
	      #endif

              
              if (!parse_ok) {
                is_error=TRUE;
                error_msg=new RWCString(ERRORS_MSG[4]);
              }
              else {

                  for (SceneObjectSymbolTable::iterator sti = _table->begin();
                       sti != _table->end();
                       sti++) {
                      AppearancePtr _app;
                      if((_app = dynamic_pointer_cast<Appearance>(sti->second))){
                          if (!_mat_table) _mat_table = new AppearanceSymbolTable;
                          else{
                              AppearanceSymbolTable::iterator _it = _mat_table->find( sti->first );
                              if(_it!=_mat_table->end())
                                  cerr << "Warning ! Multiple Definition of '" << sti->first.c_str() << "'. Overloading." << endl;
                          }
                          (*_mat_table)[sti->first]=_app;
                      }
                      else {
                          cerr << "Found not an Appearance object : '" << sti->first.c_str() << "'. Aborting." << endl;
                          error_msg=new RWCString("Found not an Appearance object.");
                          is_error=TRUE;
                          break;
                      }

                  }

                  cerr << "Done. " << endl;
                /*
                cerr << "List of object loaded : " << endl;

                Printer pp(cerr,cerr);

                for (AppearanceSymbolTable::iterator sti = _mat_table->begin();
                     sti != _mat_table->end();
                     sti++) {
                  cerr << sti->first << " = ";
                  sti->second->apply(pp);
                  cerr << endl;
                }
                */
              }

            }
          else
            {
              is_error=TRUE;
              error_msg=new RWCString(ERRORS_MSG[4]);
            }
        }
    }
  else
  {
    is_error=TRUE;
    error_msg=new RWCString(ERRORS_MSG[4]);
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg DressingFile::symbolPatternFun( RWCTokenizer next)
{

  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;
  RWCString* var_name=NULL;
  RWCString* file_name=NULL;

  if (!(token=next()).isNull())
  {
    var_name=new RWCString (token.data());

    if (!(token=next()).isNull())
    {
      if (token!="=")
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[6]);
      }
      else
      {
        if (!(token=next()).isNull())
        {
          file_name=new RWCString (token.data());
        }
        else
        {
          is_error=TRUE;
          error_msg=new RWCString (ERRORS_MSG[4]);
        }
      }
    }
    else
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[4]);
    }
  }
  else
  {
    is_error=TRUE;
    error_msg=new RWCString (ERRORS_MSG[4]);
  }

  if ((file_name) && (var_name) && (!is_error))
  {

    FSymb fsymb (*var_name,*file_name);

    if (_varTable->contains(fsymb))
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[8]);
    }
    else
    {
      _varTable->insert(fsymb);
    }
  }


  if (file_name)
  {
    delete file_name;
  }
  if (var_name)
  {
    delete var_name;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg  DressingFile::branchPatternFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;
  RWCString* file_name=NULL;

  if (!(token=next()).isNull())
  {
    // first name discarded here

    if ((token=next())!="=")
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[6]);
      }
    else {

      if (!(token=next()).isNull())
        {
          file_name=new RWCString (token.data());

          // On lit le fichier

          if (!readCrvFile(file_name->data()))
            {
              is_error=TRUE;
              error_msg=new RWCString (ERRORS_MSG[9]);
              *error_msg+=RWCString(file_name->data());
              *error_msg+=RWCString("'.");
            }
        }
      else
        {
          is_error=TRUE;
          error_msg=new RWCString (ERRORS_MSG[11]);
        }
    }
  }
  else
  {
    is_error=TRUE;
    error_msg=new RWCString (ERRORS_MSG[4]);
  }


  if (file_name)
  {
    delete file_name;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }
}

DRFErrorMsg DressingFile::minTopDiaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;
  char symbol;

  RWCString token;

  if (!(token=next()).isNull())
  {
    symbol=*token.data();
    if (!(token=next()).isNull())
    {
      if (token!="=")
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[1]);
      }
      else
      {
        if (!(token=next()).isNull())
        {
          value=atof(token.data());
        }
        else
        {
          is_error=TRUE;
          error_msg=new RWCString (ERRORS_MSG[2]);
        }
      }
    }
  }

  if (!is_error)
  {
    LibElement lb (symbol,value);
     _minTopDiaList->insert(lb);
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg DressingFile::minBotDiaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;
  char symbol;

  RWCString token;

  if (!(token=next()).isNull())
  {
    symbol=*token.data();
    if (!(token=next()).isNull())
    {
      if (token!="=")
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[1]);
      }
      else
      {
        if (!(token=next()).isNull())
        {
          value=atof(token.data());
        }
        else
        {
          is_error=TRUE;
          error_msg=new RWCString (ERRORS_MSG[2]);
        }
      }
    }
  }

  if (!is_error)
  {

     LibElement lb (symbol,value);
     _minBotDiaList->insert(lb);
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg  DressingFile::diametersUnitFun( RWCTokenizer next)
{

  ValType value;
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString(ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _diametersUnit=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg  DressingFile::azimutUnitFun( RWCTokenizer next)
{

  ValType value;
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString(ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _azimutUnit=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg  DressingFile::alphaUnitFun( RWCTokenizer next)
{

  ValType value;
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString(ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _alphaUnit=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::nbpLineFun( RWCTokenizer next)
{

  IntType value;
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atoi(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString(ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _nbpLine=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::defaultDistanceFun( RWCTokenizer next)
{

  IntType value;
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atoi(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString(ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _defaultDistance=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg  DressingFile::lengthUnitFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;


  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _lengthUnit=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg DressingFile::defaultEdgeFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  RWCString* value=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=new RWCString (token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[1]);
      }
    }

  }

  if (!is_error)
  {

    EType edge=NONE;

    if (*value==RWCString("LESS"))
    {
      edge=LESS;

    }

    if (*value=="PLUS")
    {
      edge=PLUS;
    }

    if (*value=="NONE")
    {
      edge=NONE;
    }
     _defaultEdge=edge;
  }
  else
  {
    is_error=TRUE;
    error_msg=new RWCString(ERRORS_MSG[3]);
    *error_msg+=RWCString(" `")+RWCString(*value)+RWCString("'");
  }

  if (value)
  {
    delete value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}



DRFErrorMsg  DressingFile::defaultAlphaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultAlpha=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::defaultTetaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultTeta=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg  DressingFile::defaultPhiFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultPhi=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::defaultPsiFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultPsi=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::defaultCategoryFun( RWCTokenizer next)
{
  IntType value;
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
     is_error=TRUE;
     error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atoi(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultCategory=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }
}
DRFErrorMsg  DressingFile::defaultAxeCategoryFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  IntType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atoi(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _axeDefaultCategory=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::mediumTresholdGreen( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
     is_error=TRUE;
     error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _mediumTresholdGreen=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg  DressingFile::verticilleFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  IntType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
     is_error=TRUE;
     error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atoi(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _verticille=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::mediumTresholdBlue( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
     is_error=TRUE;
     error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _mediumTresholdBlue=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}
DRFErrorMsg  DressingFile::mediumTresholdRed( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _mediumTresholdRed=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::minTresholdGreen( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _minTresholdGreen=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::minTresholdBlue( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _minTresholdBlue=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::minTresholdRed( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _minTresholdRed=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::maxTresholdGreen( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _maxTresholdGreen=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::maxTresholdBlue( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _maxTresholdBlue=value;
  }


  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::maxTresholdRed( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _maxTresholdRed=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}
DRFErrorMsg  DressingFile::elementLength(RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _elementLength=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}
DRFErrorMsg  DressingFile::deltaIndex(RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  IntType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=atoi(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _deltaIndex=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::phillotaxyFun(RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        size_t pos=token.last('/');

        if (pos==RW_NPOS)
        {
          // Il s'agit d'un angle phillotaxique

          _isIndice=FALSE;
          value=(ValType)atof(token.data());
          _phillotaxy=value;
        }
        else
        {
          _isIndice=TRUE;
          RWCString* ch_tours=new RWCString (token(0,pos));
          token.remove(0,pos);
          token.remove(0,1);
          _nbTours=atof(ch_tours->data());
          _nbLeaves=atof(token.data());
          delete ch_tours;
        }
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::formFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  RWCString token;
  IntType category;

  ListOfMyVectors point_list;
  RWCString* crv_name=NULL;

  if (!(token=next()).isNull())
  {
    category=atoi(token.data());

    if (!(token=next()).isNull())
    {
      if (token!="=")
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[1]);
      }
      else
      {
        if (!(token=next()).isNull())
        {
          crv_name=new RWCString (token.data());
          size_t index=_crvTable->index(NCrv(*crv_name));

          if (index!=RW_NPOS)
          {
            point_list=*_crvTable->at(index)._pointList;
          }
          else
          {
            error_msg=new RWCString(ERRORS_MSG[5]);
            *error_msg+=RWCString(crv_name->data())+RWCString(".");
            is_error=TRUE;
          }
        }
        else
        {
          is_error=TRUE;
          error_msg=new RWCString (ERRORS_MSG[2]);
        }
      }
    }
    else
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[4]);
    }
  }
  else
  {
    is_error=TRUE;
    error_msg=new RWCString(ERRORS_MSG[4]);
  }

  if (!is_error)
  {
    Forms* form=new BezierForm (point_list,category);
     _formsLib->addForm(*form);
  }

  if (crv_name)
  {
    delete crv_name;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::alphaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;
  AmlBoolean isAbsolute;


  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[6]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        if (token=="Absolute")
        {
          isAbsolute=TRUE;
        }
        else
        {
          if (token=="Relative")
          {
            isAbsolute=FALSE;
          }
          else
          {
            is_error=TRUE;
            error_msg=new RWCString(ERRORS_MSG[3]);
            *error_msg+=RWCString(" `")+RWCString(token.data())+RWCString("' .");
          }
        }
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString(ERRORS_MSG[4]);
      }
    }

  }

  if (!is_error)
  {
    _isAlphaRelative=!isAbsolute;
  }


  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


AmlBoolean DressingFile::readCrvFile(const char* name)
{

  AmlBoolean result=TRUE;
  RWCString file_name(name);

  ifstream file(file_name.data());

  if (!file)
  {
    result=FALSE;
  }
  else
  {
    IntType nb_curves=0;

    file >> nb_curves;

    IntType i=0;
    AmlBoolean end_of_loop=(i>=nb_curves);

    while(!end_of_loop)
    {
      char crv_name[128];

      if (file >> crv_name)
      {
        RWCString rwc_string (crv_name);

        // Read the number of points

        IntType nb_vectors=0;

        if (file >> nb_vectors)
        {
          IntType j=0;
          AmlBoolean loop2=(j>=nb_vectors);

          ListOfMyVectors point_list;

          while(!loop2)
          {
            ValType x,y,z;

            if ((file >> x ) && (file >> y ) && (file >> z ))
            {
              MyVector vect(x,y,z);
              point_list.insert(vect);

              j++;
              loop2=(j>=nb_vectors);
            }
            else
            {
              loop2=TRUE;
              result=FALSE;
            }
          }

          RWCString tmp_crv_name(crv_name);

          NCrv crv(tmp_crv_name, point_list);

          if (_crvTable->contains(crv))
          {
            cout << crv_name << " defined twice. " << endl;
          }
          else
          {
            _crvTable->insert(crv);
          }

          i++;
          end_of_loop=(i>=nb_curves);
        }
        else
        {
          result=FALSE;
          end_of_loop=TRUE;
        }
      }
      else
      {
        end_of_loop=TRUE;
        result=FALSE;
      }
    }
  }

  return result;

}

DRFErrorMsg  DressingFile::fruitSymbolFun( RWCTokenizer next)
{

  char value;
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=token.data()[0];
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString(ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _fruitSymbol=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::flowerSymbolFun( RWCTokenizer next)
{

  char value;
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=token.data()[0];
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString(ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _flowerSymbol=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::leafSymbolFun( RWCTokenizer next)
{

  char value;
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString(ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=token.data()[0];
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString(ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
    _leafSymbol=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::leafAlphaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultLeafAlpha=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}
DRFErrorMsg  DressingFile::fruitAlphaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFruitAlpha=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::flowerAlphaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFlowerAlpha=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::leafLengthFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultLeafLength=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}
DRFErrorMsg  DressingFile::fruitLengthFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFruitLength=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}


DRFErrorMsg  DressingFile::flowerLengthFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFlowerLength=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::leafBottomDiaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultLeafBottomDia=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::fruitBottomDiaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFruitBottomDia=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::flowerBottomDiaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFlowerBottomDia=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::leafTopDiaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultLeafTopDia=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::flowerTopDiaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFlowerTopDia=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}
DRFErrorMsg  DressingFile::fruitTopDiaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFruitTopDia=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}
DRFErrorMsg  DressingFile::leafBetaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultLeafBeta=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}
DRFErrorMsg  DressingFile::fruitBetaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFruitBeta=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}

DRFErrorMsg  DressingFile::flowerBetaFun( RWCTokenizer next)
{
  AmlBoolean is_error=FALSE;
  RWCString* error_msg=NULL;

  ValType value;

  RWCString token;

  if (!(token=next()).isNull())
  {
    if (token!="=")
    {
      is_error=TRUE;
      error_msg=new RWCString (ERRORS_MSG[1]);
    }
    else
    {
      if (!(token=next()).isNull())
      {
        value=(ValType)atof(token.data());
      }
      else
      {
        is_error=TRUE;
        error_msg=new RWCString (ERRORS_MSG[2]);
      }
    }

  }

  if (!is_error)
  {
     _defaultFlowerBeta=value;
  }

  if (error_msg)
  {
    DRFErrorMsg result (is_error,*error_msg);
    delete error_msg;
    return result;
  }
  else
  {
    DRFErrorMsg result;
    return result;
  }

}
ostream& DressingFile::displayOneLine(ostream& o) const {

  o << _displayMsg->data() << endl;

    return o;
}





