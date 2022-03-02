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
 *       $Id: plantframe.cpp 17611 2014-10-17 13:20:41Z pradal $
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
#include "aml/amstring.h"
#include "aml/array.h"
#include "definitions.h"
#include "plantframe.h"
#include <sys/types.h>
// #include <sys/prctl.h>
#include <time.h>
#include "tool/timer.h"
VPTOOLS_USING(Timer)


#include "linetree.h"
#include "dresser.h"
#include "correlement.h"
#include "virtualelements.h"

//#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"

#define  ERR_MSG_ARRAY          mtg_err_msgs_aml
#define  MODULE_NAME            "MTG"
extern const char *mtg_err_msgs_aml[];

#include <unistd.h>
#include <signal.h>

#include "sam_msg.h"


#include "attributes.h"

#include "geomcomputer.h"
#include "plant.h"

#include "dressingfile.h"

#ifdef _WIN32
#include <process.h>
#define execlp _execlp
#endif

using namespace std;

PlantFrame::PlantFrame(VId vertex,
                       MTG* mtg,
                       IntType level,
                       FNode* lengthf,
                       FNode* topf,
                       FNode* botf,
                       FNode* alphaf,
                       FNode* azimutf,
                       FNode* tetaf,
                       FNode* phif,
                       FNode* psif,
                       FNode* categoryf,
                       FNode* xxf,
                       FNode* yyf,
                       FNode* zzf,
                       FNode* eulerf,
                       RWCString option,
                       RWCString length_algo,
                       ValType dist,
                       const DressingFile* dressing_file,
                       ValType* translation,
                       ValType* origin,
                       FNode* digitizedf
                      )

{
  
   Timer timer;
  timer.start();
 if (dressing_file==NULL)
  {
    // We look for the default data file.

    ifstream file(DEFAULT_DRESSING_FILE_NAME);

    if (file)
    {
      _dressingFile=new DressingFile(DEFAULT_DRESSING_FILE_NAME);
    }
    else
    {
      _dressingFile=new DressingFile();
    }

    _isMyDressingFile=TRUE;
  }
  else
  {
    _isMyDressingFile=FALSE;
    _dressingFile=dressing_file;
  }


  if ((option!=SYM_MODE) && (option!=STAND_MODE) && (option!=SYMPSTAND_MODE) && (option!=NONE_MODE))
  {
    cerr << endl;
    cerr << APPL_MSG[MODE_ERR_MSG] << endl;
    cerr << endl;
    cerr << APPL_MSG[MODE_SYMP_MSG] << endl;
    cerr << APPL_MSG[MODE_STAND_MSG] << endl;
    cerr << APPL_MSG[ALL_MODES_MSG] << endl;
  }


  if ((option==SYM_MODE) || (option==SYMPSTAND_MODE))
  {
    _plant=new Plant (mtg,this,vertex,_dressingFile->getDefaultEdge(),level,SYMPODIAL,translation,origin);
  }
  else
  {
    _plant=new Plant (mtg,this,vertex,_dressingFile->getDefaultEdge(),level,NORMAL,translation,origin);
  }

  if (_plant->isAValidPlant())
  {
    IntType mtg_t;

    if ((option==STAND_MODE)|| (option==SYMPSTAND_MODE))
    {
      mtg_t=1; // On traite le mtg comme un mtg standard.
    }
    else
    {
      mtg_t=mtgType(mtg);
    }

    switch (mtg_t)
    {
    case 1:
      _geomComputer=new StandardGeom (_plant,mtg,lengthf,length_algo,topf,botf,alphaf,azimutf,categoryf,tetaf,phif,psif,eulerf,dist,_dressingFile);
      _geomComputer->computeGeometry();
      if (_geomComputer->isAValidGeometry())
      {
        _displayMessage=new RWCString(APPL_MSG[STANDARD_PF_MSG]);
      }
      else
      {
        _displayMessage=new RWCString(APPL_MSG[STANDARD_PFERR_MSG]);
      }

      break;

    case 2:
      _geomComputer=new CoordGeom (_plant,mtg,lengthf,length_algo,topf,botf,alphaf,tetaf,phif,psif,eulerf,azimutf,categoryf,xxf,yyf,zzf,TRIANGULAR,dist,_dressingFile,digitizedf);
      _geomComputer->computeGeometry();

      if (_geomComputer->isAValidGeometry())
      {
        _displayMessage=new RWCString(APPL_MSG[TRIANGULAR_MSG]);
      }
      else
      {
        _displayMessage=new RWCString(APPL_MSG[TRIANGULAR_ERR_MSG]);
      }


      break;

    case 3:
      _geomComputer=new CoordGeom (_plant,mtg,lengthf,length_algo,topf,botf,alphaf,azimutf,tetaf,phif,psif,eulerf,categoryf,xxf,yyf,zzf,CARTESIAN,dist,_dressingFile,digitizedf);
      _geomComputer->computeGeometry();

      if (_geomComputer->isAValidGeometry())
      {
        _displayMessage=new RWCString(APPL_MSG[CARTESIAN_MSG]);
      }
      else
      {
        _displayMessage=new RWCString(APPL_MSG[CARTESIAN_ERR_MSG]);
      }


      break;

    }

  }
  else
  {
     _displayMessage=new RWCString(APPL_MSG[PF_CONSTRUCTOR_ERR_MSG]);
  }

  timer.stop();
  cerr << "Computation time : " << timer.elapsedTime() << endl;
}


PlantFrame::PlantFrame(const VIdList* list_of_vertex,
                       MTG* mtg,
                       IntType level,
                       FNode* lengthf,
                       FNode* topf,
                       FNode* botf,
                       FNode* alphaf,
                       FNode* azimutf,
                       FNode* tetaf,
                       FNode* phif,
                       FNode* psif,
                       FNode* categoryf,
                       FNode* xxf,
                       FNode* yyf,
                       FNode* zzf,
                       FNode* eulerf,
                       RWCString option,
                       RWCString length_algo,
                       ValType dist,
                       const DressingFile* dressing_file,
                       ValType* origin,
                       FNode* digitizedf
                      )

{
  Timer timer;
  timer.start();
  int nb_of_vertices = list_of_vertex->entries();

  cerr << "\x0d" << "Computing plant at scale " << level << " : " << flush;
  if (dressing_file==NULL)
  {
    // We look for the default data file.

    ifstream file(DEFAULT_DRESSING_FILE_NAME);

    if (file)
    {
      _dressingFile=new DressingFile(DEFAULT_DRESSING_FILE_NAME);
    }
    else
    {
      _dressingFile=new DressingFile();
    }

    _isMyDressingFile=TRUE;
  }
  else
  {
    _isMyDressingFile=FALSE;
    _dressingFile=dressing_file;
  }


  if ((option!=SYM_MODE) && (option!=STAND_MODE) && (option!=SYMPSTAND_MODE) && (option!=NONE_MODE))
  {
    cerr << endl;
    cerr << APPL_MSG[MODE_ERR_MSG] << endl;
    cerr << endl;
    cerr << APPL_MSG[MODE_SYMP_MSG] << endl;
    cerr << APPL_MSG[MODE_STAND_MSG] << endl;
    cerr << APPL_MSG[ALL_MODES_MSG] << endl;
  }


  if ((option==SYM_MODE) || (option==SYMPSTAND_MODE))
  {
    _plant=new Plant (mtg,this,list_of_vertex,_dressingFile->getDefaultEdge(),level,SYMPODIAL, NULL, origin);
  }
  else
  {
    _plant=new Plant (mtg,this,list_of_vertex,_dressingFile->getDefaultEdge(),level,NORMAL, NULL, origin);
  }

   cerr << "\x0d" << "Plant computed ...                                   " << flush;

  if (_plant->isAValidPlant())
  {
    IntType mtg_t;

    if ((option==STAND_MODE)|| (option==SYMPSTAND_MODE))
    {
      mtg_t=1; // On traite le mtg comme un mtg standard.
    }
    else
    {
      mtg_t=mtgType(mtg);
    }

    switch (mtg_t)
    {
    case 1: // pas de ref sys pour definir les coordonnees
      _geomComputer=new StandardGeom (_plant,mtg,lengthf,length_algo,topf,botf,alphaf,azimutf,categoryf,tetaf,phif,psif,eulerf,dist,_dressingFile);
      _geomComputer->computeGeometry();
      if (_geomComputer->isAValidGeometry())
      {
        _displayMessage=new RWCString(APPL_MSG[STANDARD_PF_MSG]);
      }
      else
      {
        _displayMessage=new RWCString(APPL_MSG[STANDARD_PFERR_MSG]);
      }

      break;

    case 2: // ref sys TRIANGULAIRE
      _geomComputer=new CoordGeom (_plant,mtg,lengthf,length_algo,topf,botf,alphaf,azimutf,tetaf,phif,psif,eulerf,categoryf,xxf,yyf,zzf,TRIANGULAR,dist,_dressingFile,digitizedf);
      _geomComputer->computeGeometry();

      if (_geomComputer->isAValidGeometry())
      {
        _displayMessage=new RWCString(APPL_MSG[TRIANGULAR_MSG]);
      }
      else
      {
        _displayMessage=new RWCString(APPL_MSG[TRIANGULAR_ERR_MSG]);
      }


      break;

      case 3: // ref sys CARTESIEN
      _geomComputer=new CoordGeom (_plant,mtg,lengthf,length_algo,topf,botf,alphaf,azimutf,tetaf,phif,psif,eulerf,categoryf,xxf,yyf,zzf,CARTESIAN,dist,_dressingFile,digitizedf);
      _geomComputer->computeGeometry();

      if (_geomComputer->isAValidGeometry())
      {
        _displayMessage=new RWCString(APPL_MSG[CARTESIAN_MSG]);
      }
      else
      {
        _displayMessage=new RWCString(APPL_MSG[CARTESIAN_ERR_MSG]);
      }


      break;

    }

  }
  else
  {
     _displayMessage=new RWCString(APPL_MSG[PF_CONSTRUCTOR_ERR_MSG]);
  }
  timer.stop();
  cerr << "Computation time : " << timer.elapsedTime() << endl;


}


PlantFrame::~PlantFrame()
{
  delete _plant;

  if (_isMyDressingFile)
  {
    delete (DressingFile*) _dressingFile;
  }

  delete _displayMessage;
  delete _geomComputer;
}

void PlantFrame::coord3D(VId vertex, ValType* v) const
{
  _geomComputer->coord3D(vertex,v);
}
void PlantFrame::coord3DOrigin(VId vertex, ValType* v) const
{
  _geomComputer->coord3DOrigin(vertex,v);
}
void PlantFrame::pdir(VId vertex, ValType* v) const {
  BranchElement br = _plant->searchForElement(vertex);
  if (br.getVertex()==UNDEF)
  {
    cout << APPL_MSG[COORD_ERR] << br.getVertex() << ". " << endl;
  }
  else {
    MyVector d(br.getDirp());

    v[0] = d[0];
    v[1] = d[1];
    v[2] = d[2];

  }
}
void PlantFrame::sdir(VId vertex, ValType* v) const {
  BranchElement br = _plant->searchForElement(vertex);
  if (br.getVertex()==UNDEF)
  {
    cout << APPL_MSG[COORD_ERR] << br.getVertex() << ". " << endl;
  }
  else {
    MyVector d(br.getDirs());

    v[0] = d[0];
    v[1] = d[1];
    v[2] = d[2];

  }
}
void PlantFrame::tdir(VId vertex, ValType* v) const {
  BranchElement br = _plant->searchForElement(vertex);
  if (br.getVertex()==UNDEF)
  {
    cout << APPL_MSG[COORD_ERR] << br.getVertex() << ". " << endl;
  }
  else {
    MyVector d(br.getDirt());

    v[0] = d[0];
    v[1] = d[1];
    v[2] = d[2];

  }
}
ValType PlantFrame::length(VId vertex) const {
  BranchElement br = _plant->searchForElement(vertex);
  if (br.getVertex()==UNDEF)
  {
    cout << APPL_MSG[COORD_ERR] << br.getVertex() << ". " << endl;
    return (ValType)0;
  }
  else return br.getLength();
}
ValType PlantFrame::topDia(VId vertex) const {
  BranchElement br = _plant->searchForElement(vertex);
  if (br.getVertex()==UNDEF)
  {
    cout << APPL_MSG[COORD_ERR] << br.getVertex() << ". " << endl;
    return (ValType)0;
  }
  else return br.getTopDia();
}

ValType PlantFrame::botDia(VId vertex) const {
  BranchElement br = _plant->searchForElement(vertex);
  if (br.getVertex()==UNDEF)
  {
    cout << APPL_MSG[COORD_ERR] << br.getVertex() << ". " << endl;
    return (ValType)0;
  }
  else return br.getBotDia();
}

ValType PlantFrame::alpha(VId vertex) const {
  BranchElement br = _plant->searchForElement(vertex);
  if (br.getVertex()==UNDEF)
  {
    cout << APPL_MSG[COORD_ERR] << br.getVertex() << ". " << endl;
    return (ValType)0;
  }
  else return br.getAlpha();
}
ValType PlantFrame::beta(VId vertex) const {
  BranchElement br = _plant->searchForElement(vertex);
  if (br.getVertex()==UNDEF)
  {
    cout << APPL_MSG[COORD_ERR] << br.getVertex() << ". " << endl;
    return (ValType)0;
  }
  else return br.getBeta();
}

IntType PlantFrame::mtgType(MTG* mtg)
{
  // Look for the type of MTG which will be treat.
  // Type=1 : Standard mtg (by default).
  // Type=2 : Mtg with coordinates (triangular reference system).
  // Type=3 : Mtg with cartesian coordinates.

  IntType result=1;
  AmlBoolean end_of_loop=FALSE;
  IntType i=0;

  end_of_loop=(i>=mtg->featureNb());

  while (!end_of_loop)
  {
    if (mtg->fname(i)==TR_DAB)
    {
      if (verifyTriangRef(mtg))
      {
        result=2;
        end_of_loop=TRUE;
      }
    }

    if (mtg->fname(i)==TR_X)
    {
      if (verifyTriangRef(mtg))
      {
        result=2;
        end_of_loop=TRUE;
      }
    }

    if (mtg->fname(i)==CA_X)
    {
      if (verifyCartesianRef(mtg))
      {
        result=3;
        end_of_loop=TRUE;
      }
    }

    i++;

    if (i>=mtg->featureNb())
    {
      end_of_loop=TRUE;
    }
  }

  return result;
}

AmlBoolean PlantFrame::verifyTriangRef(MTG* mtg)
{
  // Verify if all the attributes for a triangular reference system exist

  AmlBoolean DAB,DBC,DAC,L1,L2,L3;

  DAB=DAC=DBC=L1=L2=L3=FALSE;

  for(IntType i=0;i<mtg->featureNb();i++)
  {
    if (mtg->fname(i)==TR_DAB)
    {
      DAB=TRUE;
    }

    if (mtg->fname(i)==TR_DBC)
    {
      DBC=TRUE;
    }

    if (mtg->fname(i)==TR_DAC)
    {
      DAC=TRUE;
    }

    if (mtg->fname(i)==TR_X)
    {
      L1=TRUE;
    }

    if (mtg->fname(i)==TR_Y)
    {
      L2=TRUE;
    }

    if (mtg->fname(i)==TR_Z)
    {
      L3=TRUE;
    }

  }

  AmlBoolean result=DAB && DBC && DAC && L1 && L2 && L3;

  return result;
}

AmlBoolean PlantFrame::verifyCartesianRef(MTG* mtg)
{
  // Verify if all the attributes for a triangular reference system exist

  AmlBoolean X,Y,Z;

  X=Y=Z=FALSE;

  for(IntType i=0;i<mtg->featureNb();i++)
  {
    if (mtg->fname(i)==CA_X)
    {
      X=TRUE;
    }

    if (mtg->fname(i)==CA_Y)
    {
      Y=TRUE;
    }

    if (mtg->fname(i)==CA_Z)
    {
      Z=TRUE;
    }
  }

  AmlBoolean result=X && Y && Z;

  return result;
}

void entry(void* arg) {

  if (execlp("glance","glance",(char*) arg,0)==-1)
    {
      cerr << APPL_MSG[GLANCE_MSG] << endl;
    }
}


AMObj PlantFrame::plot(GP_window&, const AMObjVector& args) const {

  if (_plant->isAValidPlant())
  {

    Dresser* dresser=new Dresser (*_plant,_dressingFile);

    int len = args.length();
    int argth = 1;


    CHECKCONDVA(len > 0,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "PlantFrame", 1));
    CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", 1, args[0].tag.string().data(), "PlantFrame"));

    FNode* interpol = 0;

    // int simplification = 0;
    FNode* filter = 0;
    FNode* color = 0;
    FNode* material = 0;
    FNode* geometry = 0;
    FNode* symbols = 0;

    bool display_on = true; // by default display the linetree

    VirtualElements* virtual_leaves=0;
    VirtualElements* virtual_fruits=0;
    VirtualElements* virtual_flowers=0;

    AMString* line_file = 0;
    RWCString* name_of_line=0;

    DressingFile* dressing_filep=NULL;

    Array* ret = new SLArray;

    while (argth < len) { // treatment of options

      // cerr << "arg = " << argth << args[argth].tag << endl;

      CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "PlantFrame", (argth+1)/2+1));

      assert(argth + 1 < len); // must contain at least two parameters : this is verified syntactically

      if (*(AMString*)(args[argth].val.p) == "Simplification") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

        CHECKCONDVA(args[argth+1].val.i > 0,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "PlantFrame", (argth+1)/2+1, "positive"));

        // simplification = args[argth+1].val.i;

      }
      else if (*(AMString*)(args[argth].val.p) == "Show" ||
               *(AMString*)(args[argth].val.p) == "Filter") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        filter = (FNode*) args[argth+1].val.p;

      }
      else if (*(AMString*)(args[argth].val.p) == "Display") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));


        RWCString display_option(*(AMString*)args[argth+1].val.p);
        if (display_option == "HIDE") display_on = false;

      }
      else if (*(AMString*)(args[argth].val.p) == "Color") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        color = (FNode*) args[argth+1].val.p;
        dresser->makeColorFun(color);

      }
      else if (*(AMString*)(args[argth].val.p) == "ColorRGB") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        color = (FNode*) args[argth+1].val.p;
        dresser->makeColorRGBFun(color);

      }
      else if (*(AMString*)(args[argth].val.p) == "Appearance") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        material = (FNode*) args[argth+1].val.p;
        dresser->makeMaterialFun(material);

      }

      else if (*(AMString*)(args[argth].val.p) == "Geometry") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        geometry = (FNode*) args[argth+1].val.p;
        dresser->makeGeometryFun(geometry);

      }

      else if (*(AMString*)(args[argth].val.p) == "DressingData") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::DRESSING_DATA,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        dressing_filep = (DressingFile*) args[argth+1].val.p;
        dresser->changeDressingFile(dressing_filep);

      }
      else if (*(AMString*)(args[argth].val.p) == "Symbols"||
               *(AMString*)(args[argth].val.p) == "Class") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        symbols = (FNode*) args[argth+1].val.p;
        dresser->makeSymbolFun(symbols);

      }

      else if (*(AMString*)(args[argth].val.p) == "VirtualFruits") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::VIRTUAL_PATTERN,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        virtual_fruits = (VirtualElements*) args[argth+1].val.p;

      }
      else if (*(AMString*)(args[argth].val.p) == "VirtualFlowers") {

	CHECKCONDVA(args[argth+1].tag() ==AMObjType::VIRTUAL_PATTERN,
		    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));
	
	virtual_flowers = (VirtualElements*) args[argth+1].val.p;
	
      }
      else if (*(AMString*)(args[argth].val.p) == "VirtualLeaves") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::VIRTUAL_PATTERN,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        virtual_leaves = (VirtualElements*) args[argth+1].val.p;

      }
      else if (*(AMString*)(args[argth].val.p) == "Interpol") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        interpol = (FNode*) args[argth+1].val.p;
        dresser->makeInterpol(interpol);

      }
#ifdef SYSTEM_IS__IRIX
      else if (*(AMString*)(args[argth].val.p) == "LineFile") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));


        line_file = (AMString*) args[argth+1].val.p;
        name_of_line=new RWCString (line_file->data());

      }
#endif
      else if (*(AMString*)(args[argth].val.p) == "MaxThreshold") {

        AMObjType t = args[argth+1].tag();

        CHECKCONDVA(t ==AMObjType::INTEGER ||
                    t ==AMObjType::REAL,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

        if (t ==AMObjType::REAL) dresser->makeMaxTreshold(args[argth+1].val.r);
        else dresser->makeMaxTreshold((ValType)args[argth+1].val.i);

      }
      else if (*(AMString*)(args[argth].val.p) == "MinThreshold") {

        AMObjType t = args[argth+1].tag();

        CHECKCONDVA(t ==AMObjType::INTEGER ||
                    t ==AMObjType::REAL,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

        if (t ==AMObjType::REAL) dresser->makeMinTreshold(args[argth+1].val.r);
        else dresser->makeMinTreshold((ValType)args[argth+1].val.i);
      }
      else if (*(AMString*)(args[argth].val.p) == "MediumThreshold") {

        AMObjType t = args[argth+1].tag();

        CHECKCONDVA(t ==AMObjType::INTEGER ||
                    t ==AMObjType::REAL,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

        if (t ==AMObjType::REAL) dresser->makeMedium(args[argth+1].val.r);
        else dresser->makeMedium((ValType)args[argth+1].val.i);

      }
      else {

        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "PlantFrame", (argth+1)/2+1));

      }

      argth += 2;

    }

    if (!name_of_line)
    {
      name_of_line=new RWCString ("line");
    }

    LineTree* linetree=new LineTree(name_of_line->data(),
                                    this,dresser,
                                    virtual_leaves,
                                    virtual_fruits,
                                    virtual_flowers);

    if (!linetree->isValid()) {
      delete linetree;
      return AMObj(AMObjType::ERROR);
    }

    linetree->viewer(filter, display_on);       // plot the linetree

#ifdef SYSTEM_IS__IRIX

    size_t pos=name_of_line->last('/');

    if (pos!=RW_NPOS) // Glance knows the location of the linetree (cf file .cfg)
    {
      name_of_line->remove(0,pos+1);
    }

    pid_t t;

    /*
    t = sproc(entry,PR_SALL, (void*)name_of_line->data());

    if (t==-1)
      {
        cerr << APPL_MSG[GLANCE_MSG2] << endl;
      }
      */

    t=fork();

    if (t==0)
    {

      if (execlp("glance","glance",name_of_line->data(),0)==-1)
      {
        cerr << APPL_MSG[GLANCE_MSG] << endl;
        exit(-1);
      }
    }
    else
    {
      if (t==-1)
      {
        cerr << APPL_MSG[GLANCE_MSG2] << endl;
      }
    }
#endif

    delete name_of_line;

    return AMObj(AMObjType::LINETREE, linetree);

  }
  else
  {
    cerr << endl;
    cerr << APPL_MSG[PLOT_MSG] << endl;
    return AMObj(AMObjType::ERROR);
  }

}


ostream& PlantFrame::displayOneLine(ostream& o) const {

  o << _displayMessage->data() << endl;

    return o;

}


