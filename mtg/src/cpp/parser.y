%{/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): Ch. Godin (christophe.godin@cirad.fr)
 *
 *       $Source$
 *       $Id: parser.y 17611 2014-10-17 13:20:41Z pradal $
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





#include <stdlib.h>
#include <iostream>
#include <fstream>

#include <assert.h>

#include "tool/util_math.h"


#include "tool/rw_cstring.h"
#include "tool/rw_hdict.h"
#include "tool/rw_vector.h"
#include "tool/rw_list.h"
//#include "tool/rw_zone.h"
//#include "tool/rw_locale.h"
//#include <rw/cstring.h>
//#include <rw/tvslist.h>
//#include <rw/tvhdict.h>
//#include <rw/tvordvec.h>
//#include <rw/zone.h>
//#include <rw/locale.h>

#include "tool/dirnames.h"
// #include "GEOM/geom_geometry.h"
// #include "GEOM/appe_appearance.h"
// #include "GEOM/scne_smbtable.h"
#include "plantgl/pgl_geometry.h"
#include "plantgl/pgl_appearance.h"
#include "plantgl/scenegraph/core/smbtable.h"
#include "plantgl/algo/codec/cdc_geom.h"

PGL_USING_NAMESPACE
VPTOOLS_USING_NAMESPACE

#include "tool/util_hashmap.h"

#include <string>

#include "mtg.h"
#include "error.h"
#include "errormsgs.h"
#include "parser_dec.h"
#include "vtxinfo.h"

static const char rcsid[] = "$Id: parser.y 17611 2014-10-17 13:20:41Z pradal $";

#if 0
#define PARSERDEBUG
#endif

typedef RWTValDlist<char> SymbList;
typedef RWTValDlistIterator<char> SymbListIter;
typedef RWTValHashDictionary<RWCString, size_t> StringIntDict;


// #define YYERROR_VERBOSE

#define CHECKIFABORT if (the_errlist->entries() >= the_errlist->maxErrorNb()) YYABORT



// ----------------------------
// Functions used by the parser
// ----------------------------

static void initParsing();
static void cleanParser();
static void REDUCING(char*);
static void STARTING(char*);
static void printAnalysisPercent();
static int createMTG(int scale_nb, ClassDef* cldef, FSetDef* fsetdef);
static void addClassDescription(ClassDef* cldef, char class1, char class2, EType reltype, int val);
static void addFeature(StringArray& featname, FTypeArray& feattype, FeatureSmbTableArray& _smbtable1,
                       char* nameval, FType typeval, void* _smbtable2);
static int findVertexByName_A(char vclass, int index, int loc, EType etype);
static int findVertexByName_B(char vclass, int index, int loc, EType etype);
static int defineVertexByName_A(char vclass_symbol, int index, VId loc, EType et);
static int defineVertexByName_B(char vclass_symbol, int index, VId loc, EType et);
static int vtxprefix(int vtx);
static void addFSet(VId v, Feature* f);
static int storeFeatureValue(int vtx, Feature* fset, int findex);


// -----------------------
// Static Global Variables
// -----------------------

static MTG* the_mtg = 0;
static int file_line_nb = 0;

static VName last_vname;

static ErrorList* the_errlist = 0;

static double old_dec_ratio = 0;

// ----------
// MTG Header
// ----------

static MTGCode mtg_code;              // code form A or B

static int class_nb = 0;
static int scale_nb = 0;

static CharArray* class_symbol = 0;
static IntArray* scale = 0;

static IntArray* vdecomp = 0;
static IntArray* vindexing = 0;
static IntArray* vdef = 0;

static ClassDef* cldef = 0;

static int feature_nb = 0;
static StringArray* featname = 0;
static FTypeArray* feattype = 0;
static FeatureSmbTableArray* smbtable_array = 0;
static FSetDef* fsetdef = 0;

static IntArray* col_name_index = 0; // gives the column nb of the ith feature.
static Feature* fset = 0;            // current set of features

// Hash Dictionary for Alias management

static size_t hashFunc(const RWCString& str) {return str.hash();}
static StringIntDict* alias_dict = 0; // mapping between vertex indexes and their aliases

// Identation management

static IntArray* indent_tbl = 0;      // index i gives the vertex stacked at identation level i
static int previous_indent_level = 0;  // current line identation level
static int current_indent_level = -1;  // current line identation level

static SymbList* symblist = 0;        // Used for storing lists of symbols (chars)

static VtxInfo* vinfo = 0;            // line nbs where a vertex occurs

// Flags positionned on the first error occuring in a certain file section

static AmlBoolean classes_flag_err = FALSE;
static AmlBoolean descrip_flag_err = FALSE;
static AmlBoolean feature_flag_err = FALSE;
static AmlBoolean mtghead_flag_err = FALSE;
static AmlBoolean code_flag_err = FALSE;

static const char* token_name[] = {

  "TokCODE",
  "TokFORM_A",
  "TokFORM_B",

  "TokCLASSES",
  "TokSYMBOL",
  "TokSCALE",
  "TokVDECOMP",
  "TokINDEXATION",
  "TokVDEF",

  "TokDESCRIPTION",
  "TokLEFT",
  "TokRIGHT",
  "TokRELTYPE",
  "TokMAX",

  "TokFEATURES",
  "TokFNAME",
  "TokFTYPE",

  "TokMTG",
  "TokENTITYCODE",

  "TokReltype",
  "TokFType",
  "TokString",
  "TokSymbol",
  "TokInteger",

  "tab",
  "eol",

  "TokError"

};


%}


%token  TokCODE
%token  TokFORM_A
%token  TokFORM_B

%token  TokCLASSES
%token  TokSYMBOL
%token  TokSCALE
%token  TokVDECOMP
%token  TokINDEXATION
%token  TokVDEF

%token  TokDESCRIPTION
%token  TokLEFT
%token  TokRIGHT
%token  TokRELTYPE
%token  TokMAX

%token  TokFEATURES
%token  TokFNAME
%token  TokFTYPE

%token  TokMTG
%token  TokENTITYCODE

%token  <etypeval> TokReltype
%token  <ftypeval> TokFType
%token  <stgval>   TokString
%token  <stgval>   TokFilename
%token  <charval>  TokSymbol
%token  <intval>   TokInteger

%token  tabc
%token  eol

%token  TokError


%union{
  int intval;
  char charval;
  CString stgval;
  void* symblistpt;  // should be of type SymbList*, but this is a parametrized type.
  const EType* etypeval;
  FType ftypeval;
  VName vname;
  Label label;
}

%start  File

%%

File :
  StartFile
  Header
  MTGDescription
  {

    if (the_errlist->entries()) YYABORT;

#ifdef PARSERDEBUG
    REDUCING("File");
#endif
  }
;

File :
  StartFile
  error
  {

    COMPLETEERRORITEM(FILEGENERALSTRUCTURE_0); // used

#ifdef PARSERDEBUG
    REDUCING("File");
#endif

    {YYABORT;}

  }
;

StartFile :
{

  initParsing();

  startStartState(); // for lex init

#ifdef PARSERDEBUG
    STARTING("File");
#endif
}
;

Header :
  StartHeader
  CodeForm
  ClassDef
  ClassDescription
  FeatureDef
  {

#ifdef PARSERDEBUG
    REDUCING("Header");
#endif
  }
;


StartHeader :
{
#ifdef PARSERDEBUG
    STARTING("Header");
#endif
}
;

/*****************************************
               CODE FORM
 *****************************************/

CodeForm :
  StartCodeForm
  TokCODE ':' tabc
  CodeFormValue LambdaTab eol
  {

#ifdef PARSERDEBUG
    REDUCING("CodeForm");
#endif
  };

CodeForm :
  StartCodeForm
  Tab
  error
  eol
  {

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CODEFORMSTX_0); // used
    CHECKIFABORT;

#ifdef PARSERDEBUG
    REDUCING("CodeForm");
#endif

    {YYABORT;}

  }
;

CodeForm :
  StartCodeForm
  TokCODE ':' tabc
  CodeFormValue
  error
  eol
  {

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;

    yyerrok;

#ifdef PARSERDEBUG
    REDUCING("CodeForm");
#endif

  }
;


CodeForm :
  StartCodeForm
  TokCODE
  error
  eol
  {

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CODEFORMSTX_0); // used
    CHECKIFABORT;

    yyerrok;

#ifdef PARSERDEBUG
    REDUCING("CodeForm");
#endif

  }
;

StartCodeForm :
{
#ifdef PARSERDEBUG
    STARTING("CodeForm");
#endif
}
;

CodeFormValue :
  StartCodeFormValue
  TokFORM_A
  {
    mtg_code = FORM_A;

#ifdef PARSERDEBUG
    REDUCING("CodeFormValue_A");
#endif
  }
 |
  StartCodeFormValue
  TokFORM_B
  {
    mtg_code = FORM_B;

#ifdef PARSERDEBUG
    REDUCING("CodeFormValue_B");
#endif
  }
;

StartCodeFormValue :
{
#ifdef PARSERDEBUG
    STARTING("CodeFormValue");
#endif
}
;


/*****************************************
            CLASS DEFINITION
 *****************************************/

ClassDef :
  StartClassDef
  ClassDefTitle
  ClassDefHead
  ClassList
  {

    if (classes_flag_err) YYABORT;

    cldef = new ClassDef(class_nb, *class_symbol, *scale, *vdecomp, *vindexing, *vdef);
    assert(cldef);
    for(int i=0; i<class_nb; i++) {
      for(int j=0; j<class_nb; j++)  {
        cldef->plus(i,j).Max() = 0;
        cldef->less(i,j).Max() = 0;
      }
    }
#ifdef PARSERDEBUG
    REDUCING("ClassDef");
#endif
  }
;

StartClassDef :
{
#ifdef PARSERDEBUG
    STARTING("ClassDef");
#endif
}
;

ClassDefTitle :
  TokCLASSES ':' LambdaTab eol
;

ClassDefTitle :
  LambdaTab error eol
  {

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDEFSTX1_0); // used
    CHECKIFABORT;

    {YYABORT;}

  }
;

ClassDefTitle :
  TokCLASSES error eol
  {

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDEFSTX1_0); // used
    CHECKIFABORT;

    yyerrok;

  }
;

ClassDefTitle :
  TokCLASSES ':' LambdaTab  error eol
  {

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

ClassDefTitle :
  TokCLASSES ':' LambdaTab  eol LambdaTab error eol
  {

    COMPLETEERRORITEM(CLASSDEFSTX2_0); // used
    CHECKIFABORT;


    {YYABORT;}

  }
;

ClassDefHead :
  TokSYMBOL tabc TokSCALE tabc TokVDECOMP tabc TokINDEXATION tabc TokVDEF LambdaTab eol
;

ClassDefHead :
  TokSYMBOL
  error
  eol
  {

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDEFSTX2_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

ClassDefHead :
  TokSYMBOL tabc TokSCALE tabc TokVDECOMP tabc TokINDEXATION tabc TokVDEF
  error
  eol
  {

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

ClassList :
  ClassList TokSymbol
  {

    if (class_symbol->contains($2)) {

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(CLASSDEFUNICITY_0); // used
      CHECKIFABORT;


    }

  }
  tabc TokInteger
  {

    if (ISFALSE($5 == ($<intval>1) || $5 == ($<intval>1+1) )) {

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(SCALEORDER_0); // used
      CHECKIFABORT;


    }

  }
  tabc TokInteger
  {

    if (ISFALSE(mtg_code == FORM_A || (mtg_code == FORM_B &&
                                       ($8 == LESSLINEAR ||
                                        $8 == NOTCONNECTED ||
                                        $8 == NONE_D)))){

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(FORMBCOND1_0); // used
      CHECKIFABORT;


    }
  }
  tabc TokInteger tabc TokInteger
  {
    class_nb++;
    class_symbol->insert($2);
    scale->insert($5);
    scale_nb = std::max(scale_nb, $5);
    vdecomp->insert($8);
    vindexing->insert($11);
    vdef->insert($13);

#ifdef PARSERDEBUG
    //REDUCING("ClassList1");
#endif
  }
  LambdaTab eol
  {
    $<intval>$ = $5;
  }
 |
  StartClassList
  TokSymbol
  {

    // First class which is analysed !

    assert(!class_symbol->contains($2));

  }
  tabc TokInteger
  {

    if (ISFALSE($5 == 0)) {

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(SCALEORDER_0); // used
      CHECKIFABORT;


    }

  }
  tabc TokInteger
  {

    if (ISFALSE(mtg_code == FORM_A || (mtg_code == FORM_B &&
                                       ($8 == LESSLINEAR ||
                                        $8 == NOTCONNECTED ||
                                        $8 == NONE_D)))) {

      classes_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(FORMBCOND1_0); // used
      CHECKIFABORT;

    }
  }
  tabc TokInteger tabc TokInteger
  {

    class_nb++;
    class_symbol->insert($2);
    scale->insert($5);
    scale_nb = std::max(scale_nb, $5);
    vdecomp->insert($8);
    vindexing->insert($11);
    vdef->insert($13);

#ifdef PARSERDEBUG
    REDUCING("ClassList2");
#endif
  }
  LambdaTab eol
  {
    $<intval>$ = $5;
  }
;

ClassList :
  ClassList
  error
  eol
  {

    class_nb++;

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

  }
 |
  error
  eol
  {

    class_nb++;

    classes_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

StartClassList :
{
#ifdef PARSERDEBUG
    STARTING("ClassList");
#endif
}
;

/*****************************************
            CLASS DESCRIPTION
 *****************************************/

ClassDescription :
  StartClassDescription
  ClassDescriptionTitle
  ClassDescriptionHead
  ClassDescriptionList
  {

    if (descrip_flag_err) YYABORT;

#ifdef PARSERDEBUG
    REDUCING("ClassDescription");
#endif
  }
;

StartClassDescription :
{
#ifdef PARSERDEBUG
    STARTING("ClassDescription");
#endif
}
;

ClassDescriptionTitle :
  TokDESCRIPTION ':' LambdaTab eol
;

ClassDescriptionTitle :
  TokDESCRIPTION error eol
  {

    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDESCSTX1_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

ClassDescriptionTitle :
  TokDESCRIPTION ':' LambdaTab  error eol
  {

    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

ClassDescriptionTitle :
  TokDESCRIPTION ':' LambdaTab  eol LambdaTab error eol
  {

    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    {YYABORT;}

  }
;

ClassDescriptionHead :
  TokLEFT tabc TokRIGHT tabc TokRELTYPE tabc TokMAX LambdaTab eol
;

ClassDescriptionHead :
  TokLEFT
  error
  eol
  {
    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(CLASSDESCSTX2_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

ClassDescriptionHead :
  TokLEFT tabc TokRIGHT tabc TokRELTYPE tabc TokMAX
  error
  eol
  {

    descrip_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

ClassDescriptionList :
  ClassDescriptionList TokSymbol
  {
    if (ISFALSE(class_symbol->contains($2))) {

      descrip_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(CLASSNOTDEFINED_0); // used
      CHECKIFABORT;


    }

  }
  tabc SymbolList tabc TokReltype tabc TokInteger LambdaTab
  {

    if (class_symbol->contains($2)) {

      SymbListIter next(*symblist);

      VClass leftc = cldef->vClass($2);
      int scaleleft = cldef->scale(leftc);

      while(next()) {

        if (cldef->isValid(next.key())) {

          VClass rightc = cldef->vClass(next.key());
          int scaleright = cldef->scale(rightc);

          if (scaleright != scaleleft) {

            descrip_flag_err = TRUE;

            yyerror(LOGICALERR);
            COMPLETEERRORITEM(TOPOLINKSCALE_0); // used
            CHECKIFABORT;

          }

          int val;

          if (*$7 == PLUS) val = cldef->plus(cldef->vClass($2),cldef->vClass(next.key())).Max();
          if (*$7 == LESS) val = cldef->less(cldef->vClass($2),cldef->vClass(next.key())).Max();

          if (ISFALSE(val == 0)) {

            RWCString param("(");

            // COMPILATION sous version 4.0 de Silicon : on est oblige de mettre
            // en commentaire les deux lignes suivantes

            param += RWCString($2);
            param += RWCString(",");
            param += RWCString(next.key());
            param += ",";
            if (*$7 == PLUS) param += "+";
            if (*$7 == LESS) param += "<";
            param += ")";

            descrip_flag_err = TRUE;

            yyerror(LOGICALERR);
            COMPLETEERRORITEM1(CLASSDESCUNICITY_1, param.data()); // used
            CHECKIFABORT;


          }
          else {

            if (ISFALSE( mtg_code == FORM_A ||
                        (mtg_code == FORM_B && (*$7 == PLUS)) ||
                        (mtg_code == FORM_B && (*$7 == LESS) && $9 <= 1))) {

              descrip_flag_err = TRUE;

              yyerror(LOGICALERR);
              COMPLETEERRORITEM(FORMBCOND2_0); // used
              CHECKIFABORT;


            }

            addClassDescription(cldef, $2, next.key(), *$7, $9);

          }

        }

      }
    }

    delete symblist;
    symblist = 0;

#ifdef PARSERDEBUG
    REDUCING("ClassDescriptionList2");
#endif
  }
  eol
 |
  /* empty */
  StartClassDescriptionList
  {
#ifdef PARSERDEBUG
    REDUCING("ClassDescriptionList1");
#endif
  }
;

ClassDescriptionList :
  ClassDescriptionList
  error
  eol
  {

    descrip_flag_err = TRUE;

    delete symblist;
    symblist = 0;

    COMPLETEERRORITEM(CLASSDESCLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

  }
 |
  Tab
  error
  eol
  {

    descrip_flag_err = TRUE;

    delete symblist;
    symblist = 0;

    COMPLETEERRORITEM(CLASSDESCLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

StartClassDescriptionList :
{
#ifdef PARSERDEBUG
    STARTING("ClassDescriptionList");
#endif
}
;

SymbolList :
  SymbolList ',' TokSymbol
  {

    if (ISFALSE(class_symbol->contains($3))) {

    descrip_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(CLASSNOTDEFINED_0); // used
      CHECKIFABORT;

    }

    symblist->append($3);
  }
 |
  TokSymbol
  {

    if (ISFALSE(class_symbol->contains($1))) {

    descrip_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(CLASSNOTDEFINED_0); // used
      CHECKIFABORT;

    }

    symblist = new SymbList;
    symblist->append($1);

  }
;

/*****************************************
            FEATURE DEFINITION
 *****************************************/

FeatureDef :
  StartFeatureDef
  FeatureDefTitle
  FeatureDefHead
  FeatureDefList
  {

    if (feature_flag_err) YYABORT;

    fsetdef = new FSetDef(feature_nb, *featname, *feattype, *smbtable_array);
    assert(fsetdef);

    // a fset is an array of features whose first element
    // contains a line number
    fset = new Feature[feature_nb];

#ifdef PARSERDEBUG
    REDUCING("FeatureDef");
#endif
  }
;

StartFeatureDef :
{
#ifdef PARSERDEBUG
    STARTING("FeatureDef");
#endif
}
;

FeatureDefTitle :
  TokFEATURES ':' LambdaTab eol
;

FeatureDefTitle :
  TokFEATURES error eol
  {

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(FEATUREDEFSTX1_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

FeatureDefTitle :
  TokFEATURES ':' LambdaTab  error eol
  {

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

FeatureDefTitle :
  TokFEATURES ':' LambdaTab  eol LambdaTab error eol
  {

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    {YYABORT;}

  }
;

FeatureDefHead :
  TokFNAME tabc TokFTYPE LambdaTab eol
;

FeatureDefHead :
  TokFNAME
  error
  eol
  {

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(FEATUREDEFSTX2_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

FeatureDefHead :
  TokFNAME tabc TokFTYPE
  error
  eol
  {

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

FeatureDefList :
  FeatureDefList FeatureLine
 |
  StartFeatureDefList
  {
#ifdef PARSERDEBUG
    REDUCING("FeatureDefList");
#endif
  }
;

FeatureLine:
  FName
  tabc FType
  LambdaTab
  eol
  {

    if (!VALID(FSetDef::checkPredefinedFeature($<stgval>1, $<ftypeval>3))) {
      feature_flag_err = TRUE;
      CHECKIFABORT;
    }

    feature_nb++;
    addFeature(*featname, *feattype, *smbtable_array, $<stgval>1, $<ftypeval>3, 0);
#ifdef PARSERDEBUG
    REDUCING("FeatureLine1");
#endif
  }
 |
  FName
  tabc FType
  tabc
  TokFilename
  LambdaTab
  eol
  {

    if (!VALID(FSetDef::checkPredefinedFeature($<stgval>1, $<ftypeval>3))) {
      feature_flag_err = TRUE;
      CHECKIFABORT;
    }

    // the name of the file must be interpreted in the local directory
    // of the mtg.

    std::string cwd = get_cwd();

    std::string mtg_name = the_mtg->_filename.data();
    std::string mtg_dir = get_dirname(mtg_name);

    // push the directory of the mtg file

    if (mtg_dir != "") {
      if (!chg_dir(mtg_dir)) std::cerr << "\tchg_dir() returned an error." << std::endl;
    }

    // Computes the symbol table as a result of parsing file whose name is $<ftypeval>5
    void* smbtable = 0;

    switch ($<ftypeval>3) {
    case GEOMETRY :
      {

        std::cerr << "Loading Geometric objects from file : " << $<stgval>5 << " ... " << std::endl;

        SceneObjectSymbolTable* geom_table = new SceneObjectSymbolTable;

        #ifdef WITH_OLD_GEOM
        bool parse_ok=SceneObject::parse($<stgval>5, std::cerr, *geom_table);
        #else
	std::string filename($<stgval>5);
        std::ifstream _file(filename.c_str());
	ScenePtr scene;
	bool parse_ok = geom_read(_file, *geom_table, scene, filename);
	#endif

        if (!parse_ok) {
          if (mtg_dir != "")
            if (!chg_dir(cwd)) std::cerr << "\tchg_dir() returned an error." << std::endl << std::endl;
          feature_flag_err = TRUE;
          yyerror(LOGICALERR);
          COMPLETEERRORITEM(FEATUREDEFLISTSTX_0);
          CHECKIFABORT;
          YYABORT;
        }

        bool strict_parsing = true;
        GeometryPtr _geom;
        for(SceneObjectSymbolTable::iterator _it = geom_table->begin();
            _it != geom_table->end(); _it++){
            _geom = dynamic_pointer_cast<Geometry>(_it->second);
            if(!_geom){
                // genMessage(WARNINGMSG(INVALID_TYPE_sss),"Geometry",_it->first.c_str(),typeid(*(_i->second)).name());
                strict_parsing = false;
            }
        }

        if(strict_parsing)
            smbtable = geom_table;
        else {
            delete geom_table;
            smbtable = 0;
        }

      }
      break;
    case APPEARANCE:
      {
        std::cerr << "Loading Material objects from file : " << $<stgval>5 << " ... " << std::endl ;

        SceneObjectSymbolTable* app_table = new SceneObjectSymbolTable;

        #ifdef WITH_OLD_GEOM
        bool parse_ok=SceneObject::parse($<stgval>5, std::cerr, *app_table);
        #else
	std::string filename($<stgval>5);
        std::ifstream _file(filename.c_str());
	ScenePtr scene;
	bool parse_ok = geom_read(_file, *app_table, scene, filename);
	#endif

        if (!parse_ok) {
          if (mtg_dir != "")
            if (!chg_dir(cwd)) std::cerr << "\tchg_dir() returned an error." << std::endl;
          feature_flag_err = TRUE;
          yyerror(LOGICALERR);
          COMPLETEERRORITEM(FEATUREDEFLISTSTX_0);
          CHECKIFABORT;
          YYABORT;
        }

        bool strict_parsing = true;
            AppearancePtr _app;
        for(SceneObjectSymbolTable::iterator _it = app_table->begin();
            _it != app_table->end(); _it++){
            _app = dynamic_pointer_cast<Appearance>(_it->second);
            if(!_app){
                // genMessage(WARNINGMSG(INVALID_TYPE_sss),"Appearance",_it->first.c_str(),typeid(*(_it->second)).name());
                strict_parsing = false;
            }
        }

        if(strict_parsing)
            smbtable = app_table;
        else{
            smbtable = 0;
            delete app_table;
        }
        /*
        std::cerr << std::endl;

        std::cerr << "MATERIAL: List of object loaded : ... " << std::flush;

        Printer pp(std::cerr,std::cerr);

        for (AppearanceSymbolTable::iterator sti = mat_table->begin();
             sti != mat_table->end();
             sti++) {
          std::cerr << sti->first << " = ";
          sti->second->apply(pp);
          std::cerr << std::endl;
        }
        std::cerr << std::endl;
        */
      }
      break;
    case GENERIC:
    {
        std::cerr << "Loading GEOM objects from file : " << $<stgval>5 << " ... " << std::endl;

        SceneObjectSymbolTable* geom_table = new SceneObjectSymbolTable;

        #ifdef WITH_OLD_GEOM
        bool parse_ok=SceneObject::parse($<stgval>5, std::cerr, *geom_table);
        #else
	std::string filename($<stgval>5);
        std::ifstream _file(filename.c_str());
	ScenePtr scene;
	bool parse_ok = geom_read(_file, *geom_table, scene, filename);
	#endif

        if (!parse_ok) {
            if (mtg_dir != "")
                if (!chg_dir(cwd)) std::cerr << "\tchg_dir() returned an error." << std::endl << std::endl;
          feature_flag_err = TRUE;
          yyerror(LOGICALERR);
          COMPLETEERRORITEM(FEATUREDEFLISTSTX_0);
          CHECKIFABORT;
          YYABORT;
        }
        smbtable = geom_table;
    }
    break;
    default:
      smbtable = 0;
      break;
    }

    // restores the current work directory

    if (mtg_dir != "")
        if (!chg_dir(cwd)) std::cerr << "\tchg_dir() returned an error." << std::endl;


    feature_nb++;
    addFeature(*featname, *feattype, *smbtable_array, $<stgval>1, $<ftypeval>3, smbtable);


#ifdef PARSERDEBUG
    REDUCING("FeatureLine2");
#endif
  }
  ;

FeatureDefList :
  FeatureDefList
  error
  eol
  {

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(FEATUREDEFLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;


#ifdef PARSERDEBUG
    //REDUCING("FeatureDefList");
#endif
  }
 |
  Tab
  error
  eol
  {

    feature_flag_err = TRUE;

    COMPLETEERRORITEM(FEATUREDEFLISTSTX_0); // used
    CHECKIFABORT;


    yyerrok;

#ifdef PARSERDEBUG
    //REDUCING("FeatureDefList");
#endif
  }
;

StartFeatureDefList :
{
#ifdef PARSERDEBUG
    STARTING("FeatureDefList");
#endif
}
;

FName :
  StartFName
  TokString
  {
    sprintf($<stgval>$,"%s",$2);

    if (featname->contains($2)) {

      feature_flag_err = TRUE;

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(FEATURENAMEUNICITY_0); // used
      CHECKIFABORT;


    }

    if (!VALID(FSetDef::checkOrderIfPredefined(featname, $2))) feature_flag_err = TRUE;


#ifdef PARSERDEBUG
    REDUCING("FName");
#endif
  }
;

StartFName :
{
#ifdef PARSERDEBUG
    STARTING("FName");
#endif
}
;

FType :
  StartFType
  TokFType
  {

    $<ftypeval>$ = $2;

#ifdef PARSERDEBUG
    REDUCING("FType");
#endif
  }
;

StartFType :
{
#ifdef PARSERDEBUG
    STARTING("FType");
#endif
}
;


/*****************************************
            MTG DESCRIPTION
 *****************************************/

MTGDescription :
  StartMTGDescription
  MTGDescriptionTitle
  MTGDescriptionHead
  ElementList
  {


#ifdef PARSERDEBUG
    REDUCING("MTGDescription");
#endif
  }
;

StartMTGDescription :
{
#ifdef PARSERDEBUG
    STARTING("MTGDescription");
#endif
}
;

MTGDescriptionTitle :
  TokMTG ':' LambdaTab eol
;


MTGDescriptionTitle :
  TokMTG error eol
  {

    mtghead_flag_err = TRUE;

    COMPLETEERRORITEM(MTGSTX1_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

MTGDescriptionTitle :
  TokMTG ':' LambdaTab  error eol
  {

    mtghead_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    yyerrok;

  }
;

MTGDescriptionTitle :
  TokMTG ':' LambdaTab  eol LambdaTab error eol
  {

    mtghead_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    {YYABORT;}

  }
;

MTGDescriptionHead :
  TokENTITYCODE
  AttributeLabels
  LambdaTab
  {

    if (ISFALSE($<intval>2 == featname->entries())) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(FEATNBDIFF_0); // used
      CHECKIFABORT;


      mtghead_flag_err = TRUE;

    }

    if (mtghead_flag_err) YYABORT;

    the_mtg->initMTG(scale_nb, cldef, fsetdef, file_line_nb);

    startCodeState();


    std::cerr << std::endl;


    // index 0 stores the line_number and does not correspond to any column
    /*
    for(int i=0; i<featname->entries(); i++) {

      std::cerr << "featname = " << (*featname)[i] << ", column = " << (*col_name_index)[i] << std::endl;

    }
    */

  }
  eol
;


MTGDescriptionHead :
  TokENTITYCODE
  error
  eol
  {

    mtghead_flag_err = TRUE;

    COMPLETEERRORITEM(UNEXPECTEDSTRING_0); // used
    CHECKIFABORT;


    {YYABORT;}

  }
;

AttributeLabels :
  AttributeLabels Tab
  TokString
  {
    // check whether this string is in the feature name array
    // find the first index of array name which contains the TokString
    int index = featname->index($<stgval>3);

    if (ISFALSE(index != RW_NPOS)) {

      mtghead_flag_err = TRUE;
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(ATTRNAME1_0); // used
      CHECKIFABORT;

    }
    else {                      // index != RW_NPOS

      // cerr << "Trying to find name of feature index = " << $<intval>1 << endl;

      if (ISFALSE( (*featname)[$<intval>1] == $<stgval>3)) {

        mtghead_flag_err = TRUE;
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(ATTRNAME2_0); // used
        CHECKIFABORT;

      }

      //cerr << " ... name found in featname = " << flush;
      //cerr << (*featname)[$<intval>1] << endl;
      //cerr << "with index = " << $<intval>1 << endl;
    }

    // cerr << "defining this name at column " << yyColumnNb() << endl;

    // Store the current column nb in association with this feature name index
    if (index>=0) {
      col_name_index->insertAt(index, yyColumnNb());
    }

    $<intval>$ = $<intval>1 + 1;

  }
 |
  /* empty */
  {


    col_name_index = new IntArray(featname->entries());
    col_name_index->insertAt(0, 1); // index 0 is index of column 1

    $<intval>$ = 0; // counts the attribute labels

  }
;

Tab:
  Tab tabc
  {
    $<intval>$ = $<intval>1 + 1;
  }
 |
  tabc
  {
    $<intval>$ = 1;
  }
;

LambdaTab :
  Tab
  {$<intval>$ = $<intval>1;}
 |
  /* empty */
  {$<intval>$ = 0;}
;



ElementList :
  ElementList Element
  {
#ifdef PARSERDEBUG
    //REDUCING("ElementList1");
#endif
  }
  |
  {
#ifdef PARSERDEBUG
    REDUCING("ElementList2");
#endif
  }
;


/*****************************************
           VERTEX  LINE
 *****************************************/


Element :
  StartElement
  VName
  {

    if ($<vname>2.ident != CHECKERROR &&
        $<vname>2.vprefix != CHECKERROR &&
        $<vname>2.label.symbol != '\0') {

      int index = featname->index("Date");
      if (index == RW_NPOS && $<vname>2.ident != UNDEF) {
        // this entity has already been defined
        // and we have no Date information => error

        int line_nb = vinfo->findFirstLine($<vname>2.ident);

#ifndef STL_EXTENSION
		char stg[20];
		std::ostrstream ost(stg,20);
		ost << line_nb;
		ost << '\0';
    
	    yyerror(LOGICALERR);
	    COMPLETEERRORITEM1(ALREADYDEFINED_1, stg); // used
#else
		std::stringstream ss;
		ss << line_nb << std::ends;
		yyerror(LOGICALERR);
        COMPLETEERRORITEM1(ALREADYDEFINED_1, ss.str().c_str()); // used
#endif
        CHECKIFABORT;

        code_flag_err = TRUE;

        $<intval>$ = CHECKERROR;
      }
      else {

        int v;

        if ($<vname>2.ident != UNDEF) {

          $<intval>$ = v = $<vname>2.ident;

          //cerr << "\nLAST VERTEX 0 = " << v << endl;
        }
        else {

          switch(mtg_code) {

          case FORM_A:
            v = defineVertexByName_A($<vname>2.label.symbol,
                                     $<vname>2.label.index,
                                     $<vname>2.vprefix,
                                     *$<vname>2.relation);
            break;

          case FORM_B:
            v = defineVertexByName_B($<vname>2.label.symbol,
                                     $<vname>2.label.index,
                                     $<vname>2.vprefix,
                                     *$<vname>2.relation);
            break;

          default:
            break;

          }
        }
        if (VALID(v)) {

#ifdef PARSERDEBUG
          std::cerr << "\n>>>>>>>>>>  Vertex EXPLICIT identifie : ident = " << v
          << ", label = " << $<vname>2.label.symbol << $<vname>2.label.index
          << ", true-loc = " << vtxprefix(v)
          << ", relation = " << *$<vname>2.relation << std::endl;
#endif

          for(int j=0; j<feature_nb; j++) fset[j].i = (unsigned long)LUNDEF;

          $<intval>$ = v;

          // cerr << "indent_tbl[" << current_indent_level <<"]= " << v << endl;

          indent_tbl->insertAt(current_indent_level, v);

          last_vname.ident = v;
          last_vname.label = $<vname>2.label;
          last_vname.relation = $<vname>2.relation;
          /*
          std::cerr << "\nLAST VERTEX 1 = " << last_vname.ident << std::endl;
          std::cerr << "\nLAST VERTEX 2 = " << $<vname>2.ident << std::endl;
          */
        }
        else {

          $<intval>$ = CHECKERROR;
        }

      }

    }
    else {

      $<intval>$ = CHECKERROR;

    }

    //startFeatureState();

  }
  FeatureList
  {

    if ($<intval>3 != CHECKERROR) {

      // featureList returns the number of matched features on that line
      if ($<vname>2.label.symbol != '\0') {

        VClass ic = cldef->vClass($<vname>2.label.symbol);

        if ((*vdef)[ic] == IMPLICIT && $<intval>4 != 0) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(IMPLICITERR_0); // used
          CHECKIFABORT;

          code_flag_err = TRUE;

        }

        int index = featname->index("Date");
        Date date = (unsigned long)LUNDEF;
        if (index != RW_NPOS) {
          date = fset[index].i;
          if ((*vdef)[ic] == EXPLICIT && date == (unsigned long)LUNDEF && code_flag_err == FALSE) {

            yyerror(LOGICALERR);
            COMPLETEERRORITEM(DATEMUSTBEDEFINED_0); // used
            CHECKIFABORT;

            code_flag_err = TRUE;

          }
        }

        vinfo->insert($<intval>3, lineNb());

        EType et = *$<vname>2.relation;

        if (et == LESSDOTLESS || et == PLUSDOTPLUS) {
          // E2<.<E5 the feature should be stored on each vtx from E2 to E5

          int index = $<vname>2.label.index;
          int loc = $<vname>2.vprefix;
          int vtxnb = index - the_mtg->vindex(loc);
          int v = $<intval>3;

          for (int i = 0; i <= vtxnb; i++) {

            addFSet(v,fset);
            v = the_mtg->vprefix(v);

          }

        }
        // create an fset only if at least one feature is defined
        else if ($<intval>4 != 0) addFSet($<intval>3, fset);

      }

    }

    //startCodeState();

#ifdef PARSERDEBUG
    REDUCING("Vertex");
#endif
  }
  eol
;


Element :
  StartElement
  VName
  error
  eol
  {

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  }
;

/* used when a relation directly after an OutSet is not followed by anything */
Element :
  StartElement
  OutSet
  TokReltype
  error
  eol
  {

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  }
;

/* used when a relation after a VName is not followed by anything */
Element :
  StartElement
  VName
  TokReltype
  error
  eol
  {

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  }
;


Element :
  StartElement
  Indentation
  '(' TokString
  error
  eol
  {

    if (!code_flag_err) {

      COMPLETEERRORITEM(MISSINGALIASPARENTH_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  }
;

Element :
  StartElement
  Indentation
  '^'
  error
  eol
  {

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  }
;

Element :
  StartElement
  Indentation
  error
  eol
  {

    if (!code_flag_err) {

      COMPLETEERRORITEM(ENTITYCODEERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

    //startCodeState();

  }
;


StartElement :
{

  code_flag_err = FALSE;

#ifdef DEBUGCHECKERROR
  printAnalysisPercent();
#endif


#ifdef PARSERDEBUG
  std::cerr << "\n***************************************************************" << std::endl;
  std::cerr << "*********************    Line " << lineNb() << "   **************************" << std::endl;
  std::cerr << "***************************************************************" << std::endl;
#endif

#ifdef PARSERDEBUG
  std::cerr << "\n\n";
  STARTING("Element");
#endif
}
;


/*****************************************
          VERTEX NAME
 *****************************************/

VName :
  VName
  TokReltype
  Label
  {

    // A ce moment il faut verifier si le vertex associe
    // a $<vname>$ existe. Si il n'existe pas: erreur
    // sinon, renvoyer l'index de ce vertex, son label, sa position et sa relation

    // vprefix and ident label.symbol and label.index can be erroneous values
    int vprefix = $<vname>1.ident;

    if ($<vname>1.label.symbol == '\0' ||
        $<vname>1.label.index == UNDEF ||
        $<label>3.symbol == '\0' ||
        $<label>3.index == UNDEF ||
        vprefix == CHECKERROR ||            // outset error
        $<vname>1.vprefix == CHECKERROR) {

      $<vname>$.ident = CHECKERROR;
      $<vname>$.label = $<label>3;
      $<vname>$.vprefix = vprefix;
      $<vname>$.relation = $<etypeval>2;

    }
    else {

      // 1. Treat the case where vprefix is UNDEF: create it

      // case of a vprefix which does not exist yet
      // and which has a valid vprefix

      EType e_type;

      if (*$<vname>1.relation == LESSDOTLESS) {

        e_type = LESSLESS;

      }
      else if (*$<vname>1.relation == PLUSDOTPLUS) {

        e_type = PLUSPLUS;

      }
      else e_type = *$<vname>1.relation;


      if (vprefix == UNDEF && $<vname>1.vprefix >=0 ) {

        switch(mtg_code) {

        case FORM_A:
          vprefix = defineVertexByName_A($<vname>1.label.symbol,
                                          $<vname>1.label.index,
                                          $<vname>1.vprefix,
                                          e_type);
          break;

        case FORM_B:
          vprefix = defineVertexByName_B($<vname>1.label.symbol,
                                          $<vname>1.label.index,
                                          $<vname>1.vprefix,
                                          e_type);
          break;

        default:
          break;

        }


#ifdef PARSERDEBUG
        if (VALID(vprefix)) {
          std::cerr << "\n>>>>>>>>>>  Vertex IMPLICIT identifie : ident = " << vprefix
          << ", label = " << $<vname>1.label.symbol << $<vname>1.label.index
          << ", true-loc = " << vtxprefix(vprefix)
          << ", relation = " << *$<vname>1.relation << std::endl;
        }
#endif

      }

#ifdef PARSERDEBUG
      std::cerr << "\n?????? Recherche d'un vertex tq: label = " << $<label>3.symbol
      << $<label>3.index << ", loc = " << vprefix
      << ", relation = " << *$<etypeval>2 << std::flush;
#endif

      int v = CHECKERROR;


      if (*$<etypeval>2 == LESSDOTLESS) {

        e_type = LESSLESS;

      }
      else if (*$<etypeval>2 == PLUSDOTPLUS) {

        e_type = PLUSPLUS;

      }
      else e_type = *$<etypeval>2;

      if (vprefix != CHECKERROR) {

        switch(mtg_code) {

        case FORM_A:
          v = findVertexByName_A($<label>3.symbol,
                                 $<label>3.index,
                                 vprefix,
                                 e_type);
          break;

        case FORM_B:
          v = findVertexByName_B($<label>3.symbol,
                                 $<label>3.index,
                                 vprefix,
                                 e_type);
          break;

        default:
          break;

        }

#ifdef PARSERDEBUG
        if (VALID(v)) std::cerr << " ... TROUVE !" << std::endl;
        else std::cerr << " ... PAS TROUVE !" << std::endl;
#endif

      } // end of if vprefix != CHECKERROR

      $<vname>$.ident = v;                  // may be an error CHECKERROR
      $<vname>$.label = $<label>3;          // label.symbol may be an error '\0'
      $<vname>$.vprefix = vprefix;          // >=0 or CHECKERROR
      $<vname>$.relation = $<etypeval>2;

    } // end of else

  }

 |

  OutSet
  TokReltype
  Label
  {

    int vprefix = $<intval>1; // may be >=0 or CHECKERROR

    if(vprefix == CHECKERROR || $<label>3.symbol == '\0' || $<label>3.index == UNDEF) {

      $<vname>$.ident = CHECKERROR;
      $<vname>$.label = $<label>3;
      $<vname>$.vprefix = vprefix;
      $<vname>$.relation = $<etypeval>2;

    }
    else {

#ifdef PARSERDEBUG
      std::cerr << "\n?????? Recherche d'un vertex tq: "
      << "label = " << $<label>3.symbol
      << $<label>3.index << ", loc = " << vprefix
      << ", relation = " << *$<etypeval>2
      << std::flush;
#endif

      int v;
      EType e_type;

      if (*$<etypeval>2 == LESSDOTLESS) {

        e_type = LESSLESS;

      }
      else if (*$<etypeval>2 == PLUSDOTPLUS) {

        e_type = PLUSPLUS;

      }
      else e_type = *$<etypeval>2;

      switch(mtg_code) {

      case FORM_A:
        v = findVertexByName_A($<label>3.symbol,
                               $<label>3.index,
                               vprefix,
                               e_type);
        break;

      case FORM_B:
        v = findVertexByName_B($<label>3.symbol,
                               $<label>3.index,
                               vprefix,
                               e_type);
        break;

      default:
        break;

      }

#ifdef PARSERDEBUG
      if (VALID(v)) std::cerr << " ... TROUVE !" << std::endl;
      else std::cerr << " ... PAS TROUVE !" << std::endl;
#endif

      $<vname>$.ident = v;                 // may be an error value UNDEF
      $<vname>$.label = $<label>3;         // label.symbol may be an error '\0'
      $<vname>$.vprefix = vprefix;         // >=0 or CHECKERROR
      $<vname>$.relation = $<etypeval>2;

    }

  }
 |
  OutSet '*'
{

  if (previous_indent_level <  current_indent_level) { // pour le cas ou il y a une *

    yyerror(LOGICALERR);
    COMPLETEERRORITEM(IDENTERR1_0); // used
    CHECKIFABORT;

    current_indent_level = previous_indent_level;

    code_flag_err = TRUE;

  }
  else {

    $<vname>$.ident = last_vname.ident;
    $<vname>$.label = last_vname.label;
    $<vname>$.vprefix = last_vname.vprefix;
    $<vname>$.relation = last_vname.relation;
  }
  // cerr << "\nLAST VERTEX = " << last_vname.ident << endl;

}
  ;


/*****************************************
                OUTSET
 *****************************************/

/*
  identation of topo code must start at column 1.
  then identation (nextline) is obliged to proceed as follows :
  - upward by incrementing the index by exactly 1
  - same level
  - downward by decreasing the index by any number so as to remain positive (>0)

  Indentation is the number of tabs before the start of the code
  (e.g. indentation = 0 if the code starts in column 1)

  Identation can be directly used as an index in the array indent_tbl;

  OutSet returns the vertex corresponding to the indentation
  or the value CHECKERROR

*/

OutSet :
  Indentation
  EscapeMarker
  {
    int indent_level = $<intval>1;

    if (ISFALSE(indent_level <= current_indent_level)) {

      if (!code_flag_err) {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(IDENTERR1_0); // used
        YYABORT; // Aborts immediately

        code_flag_err = TRUE;

      }

      $<intval>$ = CHECKERROR;

    }
    else { // retreive the last vertex with same identation level
      /*
        std::cerr << "============> indent_level     = " << indent_level << std::endl;
        std::cerr << "============> (*indent_tbl)[indent_level]  = " << (*indent_tbl)[indent_level] << std::endl;
      */
      $<intval>$ = (*indent_tbl)[indent_level];

    }

    previous_indent_level =  current_indent_level;
    current_indent_level = indent_level;

  }
 |
  Indentation
  Alias
  {

    /* An alias must be in column 1 */

    int indent_level = $<intval>1;

    if (ISFALSE(indent_level == 0)) {

      if (!code_flag_err) {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(IDENTERR2_0); // used
        CHECKIFABORT;

        code_flag_err = TRUE;

      }

      $<intval>$ = CHECKERROR;

    }
    else { // retreive the vertex corresponding to this alias

      $<intval>$ = $<intval>2; // may be an error CHECKERROR

    }

    previous_indent_level =  current_indent_level;
    current_indent_level = indent_level;
  }
 |
  Indentation
  {
    int indent_level = $<intval>1;

      if (ISFALSE(indent_level <= current_indent_level + 1)) {

        if (!code_flag_err) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(IDENTERR3_0); // used
          CHECKIFABORT;

          code_flag_err = TRUE;

        }

        $<intval>$ = CHECKERROR;

      }
      else { // retreive the last vertex with lesser (by one) indentation level

        // cerr << "============> indent_level     = " << indent_level << endl;

        if (indent_level > 0) {
          $<intval>$ = (*indent_tbl)[indent_level-1];
          // cerr << "============> (*indent_tbl)[indent_level-1]  = " << (*indent_tbl)[indent_level-1] << endl;
        }
        else  $<intval>$ = ROOT; // Root is 0

      }

    previous_indent_level =  current_indent_level;
    current_indent_level = indent_level;

/*
    if (index == RW_NPOS) {

    }
    else { // file with feature DATE defined

      // No vertex is defined on this line => return the previous vertex
      $<intval>$ = (*indent_tbl)[current_indent_level];
    }

*/

  }


;

OutSet :
  Indentation
  error
  TokReltype
  {

    if (!code_flag_err) {

      COMPLETEERRORITEM(NOTACODESTART_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyUnputToken();

    yyerrok;

    $<intval>$ = CHECKERROR;

  }
;


Indentation :
  Indentation tabc
  {
    $<intval>$ = $<intval>1 + 1;
  }
 | /* empty */
  {
    $<intval>$ = 0;
  }
;

EscapeMarker :
  '^'
;

Alias :
  '(' TokString ')'
  {
    if (alias_dict->contains($<stgval>2)) {

      $<intval>$ = (*alias_dict)[$<stgval>2]; // return the corresponding vertex id

    }
    else { /* error, alias not defined */

      if (!code_flag_err) {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(ALIASDONOTEXIST_0); // used
        CHECKIFABORT;

        code_flag_err = TRUE;

      }

      $<intval>$ = CHECKERROR;

    }

  }
;

Alias :
  '(' error ')'
  {

    if (!code_flag_err) {

      COMPLETEERRORITEM(ALIASSTRING_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    $<intval>$ = CHECKERROR;

    yyerrok;

  }
;


Label :
  TokSymbol
  {

    if (ISFALSE(class_symbol->contains($<charval>1))) {

      if (!code_flag_err) {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(CLASSERR_0); // used
        CHECKIFABORT;

        code_flag_err = TRUE;

      }

      $<charval>$ = '\0';

    }
    else $<charval>$ = $<charval>1;
  }
  TokInteger
  {

    $<label>$.symbol = $<charval>2; // contains '\0' is case of error
    $<label>$.index = $<intval>3;   // no error except a syntactic error

  }
;

Label :
  error
  TokInteger
  {

    $<label>$.symbol = '\0'; // contains '\0' is case of error
    $<label>$.index = $<intval>2;   // no error except a syntactic error

    if (!code_flag_err) {

      COMPLETEERRORITEM(CLASSERR_0); // used
      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    yyerrok;

  }
;

Label :
  TokSymbol
  error
  {

    if (!code_flag_err) {

      if (yychar != eol && yychar != tabc) {

        COMPLETEERRORITEM(INDEXERR_0); // used

        yyclearin; // clean the bad input which is kept for further scanning otherwise

      }
      else {

        COMPLETEERRORITEM(INDEXMISSING_0); // used

      }

      CHECKIFABORT;

      code_flag_err = TRUE;

    }

    $<label>$.symbol = $<charval>1; // contains '\0' is case of error
    $<label>$.index = UNDEF;   // no error except a syntactic error

    yyerrok;

  }
;


/*****************************************
             FEATURE VALUES
 *****************************************/

FeatureList :
  EmptyFeatureList {$<intval>$ = 0;}
 |FilledFeatureList {$<intval>$ = $<intval>1;}
;

EmptyFeatureList :
/* empty */
 | Tab
;


FilledFeatureList :
  FilledFeatureList tabc FeatureVal
  {

    $<intval>$ = $<intval>1 + $<intval>3;  // counts the nb of none empty featval on the line

  }
 | Tab FilledFeatureVal
  {
    $<intval>$ = 1;
  }
;

FeatureVal :
  FilledFeatureVal {$<intval>$ = 1;}
 |EmptyFeatureVal {$<intval>$ = 0;}
 ;

FilledFeatureVal :
  StartFeatureVal
  TokString
{

    int current_vertex = (*indent_tbl)[current_indent_level];

    if (strlen($<stgval>2) >= MAXSTRINGSIZE) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM1(STRINGSIZETOOBIG_1, itorwcstring(MAXSTRINGSIZE-1).data() );
      CHECKIFABORT;

    }

    int findex = col_name_index->index(columnNb()); // get the index of the feature corresponding to this column nb

    /*
    std::cerr << "findex = " << findex << std::endl;
    std::cerr << "column = " << columnNb() << std::endl;;

    for (int k = 0; k < col_name_index->entries(); k++)
    std::cerr << "index = " << k << ", col = " << (*col_name_index)[k] << std::endl;;
    */

    if (findex == RW_NPOS) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(WRONGFEATCOLUMN_0); // used
      CHECKIFABORT;

    }
    else {

      FFlag nameval = FSetDef::nameFFlag((*featname)[findex]);

      if (nameval == ALIAS_F) {

        // if this name already exists, the new value will overwrite the old one
        // => the definition of an Alias corresponds to its most recent definition in the file thread
        alias_dict->insertKeyAndValue($<stgval>2, current_vertex);

      }

      strncpy(fset[findex].s,$<stgval>2,MAXSTRINGSIZE); // \0 is copied also

      int result = storeFeatureValue(current_vertex, fset, findex);

      if(ISFALSE(result != CHECKERROR)) {

        code_flag_err = TRUE;
        CHECKIFABORT;

      }

    }

#ifdef PARSERDEBUG
    REDUCING("FeatureVal");
#endif
  }
;

EmptyFeatureVal :
  /* empty */
;

StartFeatureVal :
{
#ifdef PARSERDEBUG
    STARTING("FeatureVal");
#endif
}
;




%%

#ifdef PARSERDEBUG

static int indentcount = 0;

static void REDUCING(char* s)  {

  if (indentcount>0) indentcount--;

  std::cerr << std::endl;
  for(int i=0;i<indentcount;i++) std::cerr << "   ";
  std::cerr << "<== reducing rule: "<< s;
  if (yychar != YYEMPTY) std::cerr << ", LOOK-AHEAD = " << tokenName(yychar) << " (" << yyText() << ")";
  std::cerr << std::endl;

}

static void STARTING(char* s)  {

  std::cerr << std::endl;
  for(int i=0;i<indentcount;i++) std::cerr << "   ";
  std::cerr << "==> starting rule: "<< s;
  if (yychar != YYEMPTY) std::cerr << ", LOOK-AHEAD = " << tokenName(yychar) << " (" << yyText() << ")";
  std::cerr << std::endl;

  indentcount ++;
}

#endif

const char* tokenName(int token) {

  assert(token <= TokError);

  if (token >= TokCODE) return token_name[token-TokCODE];
  else if (token == YYEOF) return "EOF";
  else if (token == YYEMPTY) return "VOID";
  else return "UNKNOWN";

}

const char* tokenVal() {

  return yyText();

}

// These functions return the exact vprefix in terms of line and column of
// the scanning head. This takes into account the possibility of a lookahead
// reading (stored in the variable yychar).

int lineNb() {

  if (yychar != YYEMPTY)
  if (yychar == eol) return yyLineNb() - 1;
  else return yyLineNb();
  else return yyLineNb();

}

int columnNb() {

  if (yychar != YYEMPTY)
  if (yychar == tabc || yychar == eol) return yyPreviousColumnNb();
  else return yyColumnNb();
  else return yyColumnNb();

}

int firstFeatCol() {

  if (featname)
  if (featname->entries()) return (*col_name_index)[0];
  else return -1;
  else return -1;
}


const char* inputLine() {

  static char tmp[MAXLINELENGTH];

  if (yychar != YYEMPTY)
  if (yychar == eol) return yyPreviousLine();
  else if (yychar == tabc) {

    yyUnputToken(); // reject it temporarily in the input stream
    strcpy(tmp, yyCurrentLine());
    yylex(); // read again the current lookahead
    return tmp;

  }
  else return yyCurrentLine();
  else return yyCurrentLine();

}

AmlBoolean lineCodeErrorState() {

  return code_flag_err;

}

static void initParsing() {

  // cerr << "init parsing ..." << endl;

  class_symbol = new CharArray(MAXCLASSNB);
  scale = new IntArray;
  vdecomp = new IntArray;
  vindexing = new IntArray;
  vdef = new IntArray;
  featname = new StringArray(MAXFEATURENB);
  feattype = new FTypeArray(MAXFEATURENB);
  smbtable_array = new FeatureSmbTableArray(MAXFEATURENB);

  /*  Done now by the user

  // definition de la classe 0
  scale_nb++;
  class_nb++;

  class_symbol->insert('$');
  scale->insert(0);
  vdecomp->insert(FREE_D);
  vindexing->insert(FREE_I);
  vdef->insert(IMPLICIT);

  */

  alias_dict = new StringIntDict(hashFunc); // alias table giving the vextex associated to an alias
  indent_tbl = new IntArray; // vextex corresponding to a given indentation

  vinfo = new VtxInfo(file_line_nb);

  current_indent_level = -1;

}

ErrorList* getErrorList() {

  return the_errlist;

}

void cleanErrorList() {

  delete the_errlist;
  the_errlist = 0;

}

static void cleanParser() {

  // the errorList is not reset since it must be available from
  // parser outside

  // cerr << "clean parsing ..." << endl;

  lexAbort();

  the_mtg = 0;
  file_line_nb = 0;
  old_dec_ratio = 0;

  class_nb = 0;
  scale_nb = 0;
  feature_nb = 0;

  classes_flag_err = FALSE;
  descrip_flag_err = FALSE;
  feature_flag_err = FALSE;
  mtghead_flag_err = FALSE;
  code_flag_err = FALSE;

  delete alias_dict;
  delete indent_tbl;
  delete vinfo;
  alias_dict = 0;
  indent_tbl = 0;
  vinfo = 0;


  delete class_symbol;
  delete scale;
  class_symbol = 0;
  scale = 0;

  delete vdecomp;
  delete vindexing;
  delete vdef;
  vdecomp = 0;
  vindexing = 0;
  vdef = 0;

  delete featname;
  delete feattype;
  delete smbtable_array;
  featname = 0;
  feattype = 0;
  smbtable_array = 0;

  delete [] fset;
  delete col_name_index;
  fset = 0;
  col_name_index = 0;

#ifdef PARSERDEBUG
  indentcount = 0;
#endif

}

static void printAnalysisPercent() {

  double ratio = rint((lineNb() / (double) file_line_nb)*10);

  if (ratio > old_dec_ratio) {
    std::cerr << "\x0d" << "Already parsed : " << ((int) ratio)*10 << " % " << std::flush;
    old_dec_ratio = ratio;
  }

}





// ---------------------------------
// Initialisations and header update
// ---------------------------------


static void addClassDescription(ClassDef* cldef, char class1, char class2, EType reltype, int val) {

  int i = cldef->vClass(class1);
  assert(cldef->isValid(i));
  int j = cldef->vClass(class2);
  assert(cldef->isValid(j));

  if (reltype == PLUS) cldef->plus(i,j).Max() = val;
  if (reltype == LESS) cldef->less(i,j).Max() = val;

}

static void addFeature(StringArray& featname, FTypeArray& feattype, FeatureSmbTableArray& smbtable_array,
                char* nameval, FType typeval, void* smbtable) {


  featname.insert(nameval);

  feattype.insert(typeval);

  smbtable_array.insert(smbtable);

}

// ------------------------------------------
// Check for existence and Addition of vertex
// ------------------------------------------


static int vtxprefix(int vtx) {

  return the_mtg->vprefix(vtx);

}


static int findVertexByName_A(char vclass, int index, int loc, EType etype) {

  return the_mtg->findVertexByName_A(vclass, index, loc, etype);

}

static int findVertexByName_B(char vclass, int index, int loc, EType etype) {

  return the_mtg->findVertexByName_B(vclass, index, loc, etype);

}

int defineVertexByName_A(char class_symb, int index, VId loc, EType et) {


  if (et == PLUSDOTPLUS) et = PLUSPLUS;
  else if (et == LESSDOTLESS) et = LESSLESS;


  if (!VALID(the_mtg->isValidClass(class_symb))) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(CLASSERR_0);
    return CHECKERROR;
  }

  if (et == LESSLESS) {

    if (class_symb != the_mtg->classSymbol(the_mtg->vclass(loc))){
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(VTXLISTERR_0);
      return CHECKERROR;
    }

    int vtxnb = index - the_mtg->vindex(loc);

    if (vtxnb <= 0){
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(VTXLIST2ERR_0);
      return CHECKERROR;
    }

    int newvtx = loc;

    for (int i = 1; i <= vtxnb; i++) {

      newvtx = the_mtg->addVertexByName_A(class_symb, index-vtxnb+i, newvtx, LESS);

    }
    return newvtx;

  }
  else if (et == PLUSPLUS) {

    assert(class_symb == the_mtg->classSymbol(the_mtg->vclass(loc)));

    int vtxnb = index - the_mtg->vindex(loc);

    assert(vtxnb > 0);

    int newvtx = loc;

    for (int i = 1; i <= vtxnb; i++) {

      newvtx = the_mtg->addVertexByName_A(class_symb, index-vtxnb+i, newvtx, PLUS);

    }
    return newvtx;

  }
  else return the_mtg->addVertexByName_A(class_symb, index, loc, et);

}

static int defineVertexByName_B(char class_symb, int index, VId loc, EType et) {


  if (!VALID(the_mtg->isValidClass(class_symb))) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(CLASSERR_0);
    return CHECKERROR;
  }

  VId id = the_mtg->addVertexByName_B(class_symb, index, loc, et);

  return id;

}

// ------------------------------------------
//      Checking and updating features
// ------------------------------------------

// Once totally filled, the feature set f[] is stored with its vertex

static void addFSet(VId v, Feature* f) {

  // cerr << "adding fset: vid = " << v << endl;

  the_mtg->addFSet(v, f);

}


static int storeFeatureValue(int vtx, Feature* fset, int findex) {

  int type = the_mtg->fType(findex);
  unsigned long integer;
  float real;

  switch(type) {
  case DDMM:
  case DDMMYY:
  case MMYY:
  case DDMMTIME:
  case DDMMYYTIME:
    {

      integer = encodeDate(fset[findex].s, type);
      fset[findex].i = integer; // the date may be invalid (LUNDEF)

      if (integer == (unsigned long)LUNDEF) {
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(INVALIDDATE_0);

        return CHECKERROR;
      }
      else return the_mtg->checkFeature(vtx, fset, findex);

    }
  case INTEGER:
    integer = atol(fset[findex].s);
    fset[findex].i = integer;
    return the_mtg->checkFeature(vtx, fset, findex);
  case REAL:
    real = (float) atof(fset[findex].s);
    fset[findex].r = real;
    return the_mtg->checkFeature(vtx, fset, findex);
  case ALPHA:
    return the_mtg->checkFeature(vtx, fset, findex);
  case GEOMETRY:
    {
      // gets the symbol table corresponding to this feature

      SymbolTable<SceneObjectPtr>* pt = (SymbolTable<SceneObjectPtr>*)(the_mtg->fSmbTable(findex));

      // checks whether the symbolname fset[findex].s is stored in the table

      if (pt) {

        SymbolTable<SceneObjectPtr>::iterator sti = pt->find(fset[findex].s);

        if (sti != pt->end()) { // symbol is in the table

          // Store its pointer
          fset[findex].p = &(sti->second);       // void* <-- RCPTR*

          return true;

        }
        else {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
          return CHECKERROR;
        }
      }
      else {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
        return CHECKERROR;

      }

    }

  case GENERIC:
    {
      // gets the symbol table corresponding to this feature

      SymbolTable<SceneObjectPtr>* pt = (SymbolTable<SceneObjectPtr>*)(the_mtg->fSmbTable(findex));

      // checks whether the symbolname fset[findex].s is stored in the table

      if (pt) {

        SymbolTable<SceneObjectPtr>::iterator sti = pt->find(fset[findex].s);

        if (sti != pt->end()) { // symbol is in the table

          // Store its pointer
          fset[findex].p = &(sti->second);       // void* <-- RCPTR*

          return true;

        }
        else {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
          return CHECKERROR;
        }
      }
      else {

        yyerror(LOGICALERR);
        COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
        return CHECKERROR;

      }

    }

  case APPEARANCE:
    {
      // gets the symbol table corresponding to this feature

      SymbolTable<SceneObjectPtr>* pt = (SymbolTable<SceneObjectPtr>*)(the_mtg->fSmbTable(findex));

      // checks whether the symbolname fset[findex].s is stored in the table

      if (pt) {

        SymbolTable<SceneObjectPtr>::iterator sti = pt->find(fset[findex].s);

        // cerr << "Attribut nO: " << findex << " = \"" << fset[findex].s << "\"" << endl;

        if (sti != pt->end()) { // symbol is in the table

          // Store its pointer
          fset[findex].p = &(sti->second);       // void* <-- RCPTR*

          return true;

        }
        else {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
          return CHECKERROR;
        }
      }
      else {
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(UNEXPECTEDSTRING_0);
        return CHECKERROR;
      }
    }

  }

  return CHECKERROR; // Should return before

}


// --------------
// Parsing Errors
// --------------

static const int MAXERRMESSAGELENGTH = 500;

char* LOGICALERR = "logical error";

/* Remplit line_contents avec le contenu de la ligne courante
   On est oblige d'aller lire la ligne dans le fichier original
   puisque la ligne est en cours d'analyse et n'a peut etre pas
   ete completement analysee a ce moment */

static void getCompleteLine(int number, char* line_contents) {

  register long i, lnbegin;
  long int pos = ftell(yyin);

  fseek(yyin, 0, SEEK_SET);
  for(i=0;i<number;i++) {
    lnbegin = ftell(yyin);
    fgets(line_contents, MAXLINELENGTH, yyin);
  }

  fseek(yyin, pos, SEEK_SET);

}

// creates a new error item containing at least:
// - the type of the error
// - the line and column number of the error
// - the state of the current line when the error occurs

int yyerror(char* errtype) {

  assert(errtype);

  if (!lineCodeErrorState()) { // if not yet any error in this entity-code, create one

    char complete_line[MAXLINELENGTH];

    ErrorType type = GENERAL;

    getCompleteLine(lineNb(), complete_line);

    the_errlist->insert(ErrorItem(
#ifdef DEBUGCHECKERROR
                              NULL,
                              0,
                              yychar,
#endif
                              "Empty Message ...",
                              type,
                              UNDEF,
                              lineNb(),
                              columnNb(),
                              inputLine(),
                              complete_line,
                              UNDEF,
                              UNDEF
                              )
                    );

    if (yychar == 0) { // corresponds to the end of file
      COMPLETEERRORITEM(FILEENDSPREMATURELY_0);
    }

    /*
       std::cerr << "line = " << lineNb() << std::endl;
       cerr << "col  = " << columnNb() << std::endl;
       cerr << "input line = \"" << inputLine() << "\"" << std::endl;
       */

  }
  return 1;

}


// ----------------------
// MTG parser entry point
// ----------------------

ErrorList* parseMTG(MTG* mtg, int line_nb, std::ostream& errfile, int maxerrnb) {

  the_mtg = mtg;
  file_line_nb = line_nb;

  cleanErrorList(); // clean the previous errorlist before creating a new one.
  the_errlist = new ErrorList(err_messages, err_types, errfile, maxerrnb);

  yyparse();
  cleanParser();

  return the_errlist;

}
