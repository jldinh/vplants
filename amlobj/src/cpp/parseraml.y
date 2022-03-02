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
 *       $Id: parseraml.y 17611 2014-10-17 13:20:41Z pradal $
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




// #define QT_AML



#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <stack>
#include <queue>

#include <string>
#include <assert.h>

#include "tool/config.h"
#ifdef STL_EXTENSION
#include <sstream>
#include <strstream>
#endif
//#include <rw/regexp.h>

#include "readline.h"
#include "scanneraml.h"
#include "parseraml.h"
#include "fnode.h"
#include "amstring.h"

#include "array.h"
  //#include "kernel_funs.h"
#include "kernel_err.h"
#include "erroraml.h"
#include "release.h"

#include "tool/dirnames.h"

#ifdef QT_AML
#include "qt_aml.h"
#endif

VPTOOLS_USING_NAMESPACE
using namespace std;

/* constantes et Variables globales */

#define  ERR_MSG_ARRAY          parser_err_msgs_aml
#define  MODULE_NAME            "AML Parser"

typedef enum PARSER_ERRORLABEL {
  PARSER_SYNTAX_ERROR = KERNEL_ERR_OFFSET,
  ARGLIST_ERR_d,
  ARGLIST_NB_ERR_sd,
  ARGLIST_FUNC_ERR_d,
  FUNCDEF_FREEVAR_ERR,
  FUNCDEF_FREEVAR2_ERR_s,
  FUNCDEF_UNDEF_FREEVAR_ERR_s,
  FUNCDEF_RH_ERR,
  FUNCDEF_NOARG_ERR,
  FUNCDEF_RECURSIVE_DEF_ERR_s
};



// variables static

static const char *parser_err_msgs_aml[] = {

  "Syntax error",
  "Argument list: argument %d: error",                                                            // ARGLIST_ERR_d
  "Argument list: function %s: %d argument(s): bad nb of argument(s)",                            // ARGLIST_NB_ERR_sd
  "Argument list: argument %d: a function is not allowed as an argument",                         // ARGLIST_FUNC_ERR_d
  "Function definition: left-hand member should only contain arguments which are free-variables", // FUNCDEF_FREEVAR_ERR
  "Function definition: free-variable %s appears twice in the left-hand member",                  // FUNCDEF_FREEVAR2_ERR_s
  "Function definition: free-variable %s does not appear in the left-hand member",                // FUNCDEF_UNDEF_FREEVAR_ERR_s
  "Function definition: error in the right-hand member",                                        // FUNCDEF_RH_ERR
  "Function definition: a function with no argument is not allowed",                            // FUNCDEF_NOARG_ERR
  "Function definition: name %s cannot be used as a variable in a recursive definition"         // FUNCDEF_RECURSIVE_DEF_ERR_s
};

#ifdef _WIN32
static const char* LOG_FILE = "aml.log";
#else
static const char* LOG_FILE = ".amlog";
#endif

static std::ostream* aml_output_stream = 0;

static char input_buff[MAXLINELENGTH];
static std::ifstream* input_stream = 0;
static std::ofstream* log_file = 0;
static AMLErrorList* errlist = 0;

static AmlBoolean AMLECHO = TRUE;

// ----------------------------
// static functions declaration
// ----------------------------

static NextLineFunc AMLGetNextLine;
static int getNextLine();
static StringList* makeFreeVarList(const FAMObjPtrList*);
static AmlBoolean matchVarLists(const StringList* list1, const StringList* list2, int* result);
static FAMObj* eval(RWCString, const FAMObjPtrList&);
static FAMObj* iter_eval(RWCString, const FAMObjPtrList&, RWCString);
static void printErrorList();
static AmlBoolean anyErrors();

static const char* token_name[] = {

"TokSystemCall",
"TokInt",
"TokReal",
"TokCharacter",
"TokName",
"TokString",
"TokFreeVar",

"eol",

"TokDO",
"TokFOREACH",
"TokWHILE",
"TokSWITCH",
"TokCASE",
"TokDEFAULT",

"TokIF",
"TokTHEN",
"TokELSE",

"TokIN",
"TokINCLUDE",
"TokRIGHTARROW",

"TokOR", "TokUNION", "TokINTER", "TokSETMINUS",
"TokAND",
"TokLT", "TokLTEQ", "TokGT", "TokGTEQ",
"TokDIFF", "TokEQ",
"TokNOT",

"TokAT",

"TokMINUS", "TokPLUS",
"TokTIMES", "TokSLASH",
"TokMOD",
"TokPOWER",
"UMINUS",
"TokQUOTE",

"TokBYE",
"TokError"

};

%}

%union {
  int           integer;
  int           boolean;
  double        real;
  char          character;
  char*         String;
  AMObj*        pamobj;
  FAMObj*       pfamobj;
  FAMObjPtrList* famobjptrlist;
  StringList*   stringlist;
}

%token <String>    TokSystemCall
%token <integer>   TokInt
%token <real>      TokReal
%token <character> TokCharacter         /*e.g.  'A'   */
%token <String>    TokName              /*e.g.  Val in exp such as Val(X) */
%token <String>    TokString            /*e.g.  "cut" */
%token <String>    TokFreeVar

%left ';'
%right '='
%left '?'
%left ':'
%left ','

%token eol

%left TokDO
%token TokFOREACH
%token TokWHILE
%token TokSWITCH
%token TokCASE
%token TokDEFAULT

%token TokIF
%token TokTHEN
%right TokELSE
%token TokINCLUDE

%right TokIN
%right TokRIGHTARROW

%left TokOR TokUNION TokINTER TokSETMINUS
%left TokAND
%left TokLT TokLTEQ TokGT TokGTEQ
%left TokDIFF TokEQ
%left TokNOT

%left TokAT

%left TokMINUS TokPLUS
%left TokTIMES TokSLASH
%right TokMOD
%left TokPOWER
%left UMINUS
%left TokQUOTE

%token TokBYE
%token TokError

%type <pamobj>  Atom
%type <pfamobj> FExp
%type <pfamobj> DefaultCase
%type <famobjptrlist>   FExpList
%type <famobjptrlist>   CaseList
%type <famobjptrlist>   CaseList1
%type <famobjptrlist>   FilledFExpList
%type <famobjptrlist>   OptionalFExpList

%start Session

%%

Session :
  CommandList Bye
;

CommandList :
  CommandList Command
  {
    if (!getNextLine()) YYACCEPT;
  }
 |
  {
    if (!getNextLine()) YYACCEPT;
  }
;

Bye :
 TokBYE;

Command :
  FExp eol
  {

    if ($1) {

      if (anyErrors()) {

        printErrorList();

      }
      else {
        if (AMLECHO) {

          AMLOUTPUT << std::endl;
          AMLOUTPUT << *(AMObj*)$1 << std::endl; // echoes the evaluation
          AMLOUTPUT << std::endl;

        }

      }

      // removes the variable list and the objects pointed to by $1->val.p if any,
      // except for objects in AMObjTable

      delete $1;

    }

  }
 |
  eol
;


Command :
  error eol
  {
    AMLCOMPLETEERRORITEM(PARSER_SYNTAX_ERROR);

    printErrorList();

    yyclearin;
    yyerrok;

  }
;
Command :
  TokName error eol
  {
    RWCString name($1);
    amobjTable()->remove(name);

    AMLCOMPLETEERRORITEM(PARSER_SYNTAX_ERROR);

    printErrorList();

    yyclearin;
    yyerrok;

  }
;
/***************/
/* expressions */
/***************/

/*
   FExp return a FAMObj* on a valid FAMObj.
   the FAMObj has
     - a type (here FNODE or VAR or ATOM)
     - a value (here a pointer to the FNode at hand, the variable name, or the atom value)
     - a freevariable list in case where type is FNODE
*/

FExp :
 Atom
  {
    $$ = new FAMObj(*($1)); // arglist = 0
    delete $1;
  }
|TokSystemCall
  {
    int result = system($1);

    delete [] $1;

    if (result == -1) aml_system_error(AMLOUTPUT , "Command Failed");

    $$ = new FAMObj(AMObj(AMObjType::VOID));

  }

|TokFreeVar
  {
    StringList* list = new StringList;
    list->insert($1);           // char* copied in a RWCString
    $$ = new FAMObj(AMObj(AMObjType::VAR, new AMString($1)), list);
    delete [] $1;
  }
|TokQUOTE TokName
  {

    RWCString fname($2);
    delete [] $2;

    $$ = new FAMObj(AMObj(AMObjType::STRING, new AMString(fname))); // arglist == 0

  }
|TokName        /* to give a named expression */
  {

    AMObj amobj;
    RWCString fname($1);
    delete [] $1;

    AmlBoolean testintable = FALSE;

    if (amobjTable()->contains(fname)) {
      testintable = TRUE;
    }
    else {
      fname.prepend(SYSTEMCHAR);
      if (amobjTable()->contains(fname)) {
        testintable = TRUE;
      }
    }

    if (testintable) {

      amobjTable()->findValue(fname, amobj);

      if (amobj.tag == AMObjType::FNODE && !((FNode*)amobj.val.p)->isValid()) {

        genAMLError(ERRORMSG(FUNCDEF_RECURSIVE_DEF_ERR_s), fname.data());

        $$ = new FAMObj(AMObj(AMObjType::ERROR));

      }
      else $$ = new FAMObj(amobj);      // arglist == 0

    }
    else {

      // What is not is the AMObjTable must be a simple name
      // since FExp in certain cases (such as TokName TokRIGHTARROW FExp)
      // can be a name e.g. ASCII in Display(_x, Type -> ASCII)

      $$ = new FAMObj(AMObj(
                            AMObjType::STRING,
                            new AMString(
                                         RWCString(fname.strip(RWCString::leading,':'))
                                         )
                            )); // arglist == 0

    }

  }
|TokName '=' FExp
  {

    FAMObjPtrList list;

    FAMObj* ptfam = new FAMObj(AMObj(AMObjType::STRING, new AMString($1)));

    list.insert(ptfam);
    list.insert($3);

    $$ = eval("=", list);

    delete ptfam;

    delete [] $1;
    delete $3;

  }
|TokName '(' FExpList ')'
  {

    RWCString name($1);

    /* make the union of variables _x, _y, _z in $3 */

    FAMObjPtrListIter next(*$3);
    StringList* arglist = new StringList;
    AmlBoolean error_flag = FALSE;
    while (next()) {
      FAMObj* famobj = next.key();
      if (!error_flag) {
        if (famobj->tag.type != AMObjType::VAR) {
          genAMLError(ERRORMSG(FUNCDEF_FREEVAR_ERR));
          error_flag = TRUE;
        }
        else {
          if (arglist->contains(*(AMString*)(famobj->val.p))) {
            genAMLError(ERRORMSG(FUNCDEF_FREEVAR2_ERR_s), (*(AMString*)(famobj->val.p)).data());
            error_flag = TRUE;
          }
          else arglist->insert(*(AMString*)(famobj->val.p));
        }
      }
      delete famobj; // won't be reused in the following
    }

    delete $3;

    if (!error_flag) {

      // insert the function profile in the AMObjTable

      AMObj obj;
      int found = amobjTable()->findValue(name, obj);

      if (found && obj.tag == AMObjType::FNODE) {

        AMLOUTPUT << std::endl << "Overwritting existing object :" << name << std::endl;

      }
      else { // put the symbol in the symbol table for potential recursive calls

        AMObj obj(AMObjType::FNODE, new FNode(name.data(), arglist->entries())); // builds an invalid FNode with $1 as a name
        amobjTable()->insert(name, obj);                  // this FNode has to be patched afterwards

      }

      $<stringlist>$ = arglist;

    }
    else { // error in th arglist

      delete arglist;

      $<stringlist>$ = 0;

    }

  }
  '=' FExp   /* FExpList should be made only of TokFreeVar */
  {

    assert($7);

    RWCString name($1);
    delete [] $1;

    StringList* arglist = $<stringlist>5;

    if (arglist) {

      AMObj* pobj;

      int varnb = arglist->entries();

      if ($7->tag == AMObjType::ERROR || $7->tag == AMObjType::UNDEF) {

        amobjTable()->remove(name);

        genAMLError(ERRORMSG(FUNCDEF_RH_ERR));

        $$ = new FAMObj(AMObj(AMObjType::ERROR));

      }
      else {

        if (varnb > 0) { // definition of a function with at least one argument

          int* imatch = new int[varnb];

          AmlBoolean res;
          int rightvarnb = $7->arglist ? $7->arglist->entries(): 0;

          if (rightvarnb) res = matchVarLists(arglist, $7->arglist, imatch);
          else res = TRUE;

          if (FAILCOND(res)) {

            RWCString freevars;

            StringListIter next(*(StringList*) $7->arglist);
            int index;
            while (next()) {
              index = arglist->index(next.key());
              if (index == RW_NPOS) {
                freevars += next.key();
                freevars += " ";
              }
            }

            amobjTable()->remove(name);
            genAMLError(ERRORMSG(FUNCDEF_UNDEF_FREEVAR_ERR_s), freevars.data());

            $$ = new FAMObj(AMObj(AMObjType::ERROR));

          }
          else {

            pobj = &((*amobjTable())[name]); // the function already exists in the table partially defined

            if ($7->tag == AMObjType::FNODE) {

              ((FNode*)$7->val.p)->giveName(name, varnb, imatch); // complete FExp with name and varlist

              *(FNode*)pobj->val.p = *(FNode*)$7->val.p;

            }
            else if ($7->tag == AMObjType::VAR) { // Function Identity(_x) = _x

              FAMObjPtrList list;
              list.insert($7);

              FAMObj* id = eval("Identity", list);
              assert(id);

              ((FNode*) id->val.p)->giveName(name, varnb, imatch);

              *(FNode*)pobj->val.p = *(FNode*)id->val.p;

              delete id;

            }
            else { // constant function : $7->tag == AMObjType::'ATOM'

              FAMObjPtrList list;
              list.insert($7);

              AMObj headfun;

              amobjTable()->findValue(":Identity", headfun);

              assert(headfun.tag == AMObjType::FNODE);
              assert(headfun.val.p);

              StringList* varlist = new StringList; // empty list of free variables

              FNode* fun = new FNode("", (FNode*)headfun.val.p, varlist, &list);
              assert(fun->isValid());
              // FAMObj(AMObj(AMObjType::FNODE, fun), varlist) un one step
              // doesnot call the destructor of the AMObj !!!!!

              FAMObj* id;
              {
                AMObj tmpobj(AMObjType::FNODE, fun);

                id =  new FAMObj(tmpobj, varlist);
              }
              // if this last paren is placed after *(FNode*)pobj->val.p = *(FNode*)id->val.p;
              // the destruction of the temporary object is not done correctly anymore

              ((FNode*) id->val.p)->giveName(name, varnb, imatch);

              *(FNode*)pobj->val.p = *(FNode*)id->val.p;

              delete id;

            }

            $$ = new FAMObj(*pobj);

          }

          delete [] imatch;

        }
        else { // definition of a variable

          amobjTable()->remove(name);
          genAMLError(ERRORMSG(FUNCDEF_NOARG_ERR));

          $$ = new FAMObj(AMObj(AMObjType::ERROR));

        }

      }

      delete arglist;

    }
    else { // arglist error occured

      amobjTable()->remove(name);

      // an error has been generated in during the analysis of the arglist

      $$ = new FAMObj(AMObjType::ERROR);

    }

    delete $7;

  }
|TokName '(' FExpList ')'
  {

    assert($3); // arglist should not be empty

    RWCString name($1);
    delete [] $1;

    $$ = eval(name, *$3);

    // Modif pour parser un fichier correspondant a un tableau
    /*
    if (name == "Save" && (*$3).entries() >=2) {
      AMObj obj = *((*$3)[0]);      // AMObj = FAMObj ! premier argument de la liste
      AMObj filename = *((*$3)[1]);      // nom du fichier = second argument de la liste

      if (filename->tag == AMObjType::STRING) {


      }

    }
    */

    FAMObjPtrListIter next(*$3);

    while (next()) {
      delete next.key();
    }

    delete $3;



  }
 | '[' FExpList ']'
  {

    assert($2); // arglist should not be empty

    $$ = eval("[]", *$2);

    FAMObjPtrListIter next(*$2);

    while (next()) {
      delete next.key();
    }

    delete $2;

  }
 | FExp TokAT FExp
  {

    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("@", list);

    delete $1;
    delete $3;

  }
 | FExp TokUNION FExp
  {

    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("|", list);

    delete $1;
    delete $3;

  }
 | FExp TokINTER FExp
  {

    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("&", list);

    delete $1;
    delete $3;

  }
 | FExp TokSETMINUS FExp
  {

    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("\\", list);

    delete $1;
    delete $3;

  }
|FExp TokPLUS FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("+", list);

    delete $1;
    delete $3;

  }
|FExp TokMINUS FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("-", list);

    delete $1;
    delete $3;

  }
|FExp TokTIMES FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("*", list);

    delete $1;
    delete $3;

  }
|FExp TokSLASH FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("/", list);

    delete $1;
    delete $3;

  }
|FExp TokPOWER FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("^", list);

    delete $1;
    delete $3;

  }
|FExp TokMOD FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("Mod", list);

    delete $1;
    delete $3;

  }
|FExp TokEQ FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("==", list);

    delete $1;
    delete $3;

  }
|FExp TokDIFF FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("!=", list);

    delete $1;
    delete $3;

  }
|FExp TokAND FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("And", list);

    delete $1;
    delete $3;

  }
|FExp TokOR FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("Or", list);

    delete $1;
    delete $3;

  }
|FExp TokLT FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("<", list);

    delete $1;
    delete $3;

  }
|FExp TokLTEQ FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval("<=", list);

    delete $1;
    delete $3;

  }
|FExp TokGT FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval(">", list);

    delete $1;
    delete $3;

  }
|FExp TokGTEQ FExp
  {
    FAMObjPtrList list;
    list.insert($1);
    list.insert($3);

    $$ = eval(">=", list);

    delete $1;
    delete $3;

  }
|TokNOT FExp
  {
    FAMObjPtrList list;
    list.insert($2);

    $$ = eval("Not", list);

    delete $2;

  }
|TokMINUS FExp %prec UMINUS
  {

    FAMObjPtrList list;
    list.insert($2);

    $$ = eval("Unary-", list);

    delete $2;

  }
|'?' TokName
  {
    FAMObjPtrList list;

    FAMObj* ptfam = new FAMObj(AMObj(AMObjType::STRING, new AMString($2)));
    delete [] $2;

    list.insert(ptfam);

    $$ = eval("?name", list);

    delete ptfam;

  }
|'?'
  {
    FAMObjPtrList list;

    $$ = eval("?user", list);

  }
|'?' '?'
  {
    FAMObjPtrList list;

    $$ = eval("?all", list);

  }
| TokIF FExp TokTHEN FExp TokELSE FExp
{

  FAMObjPtrList list;
  list.insert($2);
  list.insert($4);
  list.insert($6);

  $$ = eval("IfThenElse", list);

  delete $2;
  delete $4;
  delete $6;

}
| TokWHILE FExp TokDO FExp
{

  FAMObjPtrList list;
  list.insert($2);
  list.insert($4);

  AMLOUTPUT << "Control by While Not Yet Implemented" << std::endl;

  // $$ = eval("While", list);

  delete $2;
  delete $4;

}
| TokSWITCH FExp CaseList
{

  assert($3); // Caselist should exists

  $3->prepend($2);

  $$ = eval("Switch", *$3);

  FAMObjPtrListIter next(*$3);

  while (next()) {
    delete next.key();
  }

  delete $3;

}
|'[' FExp ':' FExp ']' /* interval --> liste constructor */
{

  FAMObjPtrList list;
  list.insert($2);
  list.insert($4);

  $$ = eval("Interval", list);

  delete $2;
  delete $4;

}
|FExp ';' FExp
{

  FAMObjPtrList list;
  list.insert($1);
  list.insert($3);

  $$ = eval("ExpSequence", list);

  delete $1;
  delete $3;

}
|'[' FExp ':' FExp ':' FExp ']' /* interval --> liste constructor */
{

  FAMObjPtrList list;
  list.insert($2);
  list.insert($4);
  list.insert($6);

  $$ = eval("Interval", list);

  delete $2;
  delete $4;
  delete $6;

}
|TokFOREACH FExp TokIN FExp ':' FExp
{

  assert($2);

  if (FAILCOND($2->tag == AMObjType::VAR)) {

    genAMLError(ERRORMSG(K_ITER_ARG_TYPE_ERR_sdss), "Foreach .. In .. : ..", 1, $2->tag.string().data(), "free variable");

    $$ = new FAMObj(AMObj(AMObjType::ERROR));

  }
  else {

    RWCString tiedvar(*(AMString*)($2->val.p));

    if (FAILCOND(!$4->arglist || !$4->arglist->contains(tiedvar))) {

      RWCString alpha("defined without the tied variable ");
      alpha += tiedvar;

      genAMLError(ERRORMSG(K_ITER_ARG_TYPE_ERR_sdss), "Foreach .. In .. : ..", 2, "FUNC", alpha.data());
      $$ = new FAMObj(AMObj(AMObjType::ERROR));

    }
    else {

      FAMObjPtrList list;
      list.insert($4);
      list.insert($6);

      $$ = iter_eval(":Foreach", list, tiedvar);

    }
  }

  delete $2;
  delete $4;
  delete $6;

}
|'(' FExp ')' {$$ = $2;}
;

CaseList :
  CaseList1 DefaultCase
  {

    $1->insert($2);

    $$ = $1;

  }
;

CaseList1 :
  CaseList1 TokCASE FExp ':' FExp
  {

    $1->insert($3);
    $1->insert($5);

    $$ = $1;

  }
 |TokCASE FExp ':' FExp
  {

    $$ = new FAMObjPtrList;

    $$->insert($2);
    $$->insert($4);

  }
;


DefaultCase :
  TokDEFAULT ':' FExp
  {
    $$ = $3;
  }
;

FExpList :
  FilledFExpList {$$ = $1;}
 |OptionalFExpList {$$ = $1;}
 |FilledFExpList ',' OptionalFExpList
  {

    FAMObjPtrListIter next(*$3);

    while (next()) {

      $1->insert(next.key());

    }

    delete $3;

    $$ = $1;

  }
 |/*empty*/{$$ = new FAMObjPtrList;}
;

FilledFExpList :
  FilledFExpList ',' FExp
  {

    $1->insert($3);

    $$ = $1;

  }
 |FExp
  {

    $$ = new FAMObjPtrList;

    $$->insert($1);

  }
;

OptionalFExpList :
  OptionalFExpList ',' TokName TokRIGHTARROW FExp
  {

    $1->insert(new FAMObj(AMObj(AMObjType::OPTION, new AMString($3))));
    delete [] $3;

    $1->insert($5);

    $$ = $1;

  }
 |TokName TokRIGHTARROW FExp
  {

    $$ = new FAMObjPtrList;

    $$->insert(new FAMObj(AMObj(AMObjType::OPTION, new AMString($1))));
    delete [] $1;

    $$->insert($3);

  }
;


Atom :
  TokInt {$$ = new AMObj(AMObjType::INTEGER, $1);}
 |TokReal {$$ = new AMObj(AMObjType::REAL, $1);}
 |TokString {$$ = new AMObj(AMObjType::STRING, new AMString($1)); delete [] $1;}
 |TokCharacter {$$ = new AMObj(AMObjType::CHAR, $1);}
;



%%

static AmlBoolean checkEvalArgListValidity(const FAMObjPtrList& list) {

  FAMObjPtrListIter next((FAMObjPtrList&)list);

  while (next()) {

    if (next.key()->tag == AMObjType::ERROR) {
      // genAMLError(ERRORMSG(ARGLIST_ERR_d), list.entries());
      return FALSE;
    }
    /*
    if (next.key()->tag == AMObjType::FNODE) {
      genAMLError(ERRORMSG(ARGLIST_FUNC_ERR_d), list.entries());
      return FALSE;
    }
    */
  }

  return TRUE;

}

static AmlBoolean checkIterEvalArgListValidity(const FAMObjPtrList& list) {

  FAMObjPtrListIter next((FAMObjPtrList&)list);

  while (next()) {

    if (next.key()->tag == AMObjType::ERROR) {
      // genAMLError(ERRORMSG(ARGLIST_ERR_d), list.entries());
      return FALSE;
    }

  }

  return TRUE;

}

// ----------------
// static functions
// ----------------

// Create a new FAMObj which can be
// - a FNode : this object has then to be destroyed by the toplevel FNode
// - something which is not an FNode, which has then to be cleared and destroyed after use

static FAMObj* eval(RWCString fname, const FAMObjPtrList& list) {

  FAMObj* retval;

  // If there exists an error in the argument list abort here
  if (!(checkEvalArgListValidity(list))){

    return new FAMObj(AMObj(AMObjType::ERROR));

  }

  int testintable = 0; // FALSE

  if (amobjTable()->contains(fname)) {
    testintable = 1;                            // Not a system function
  }
  else {
    fname.prepend(SYSTEMCHAR);
    if (amobjTable()->contains(fname)) {
      testintable = 2;                          // System function
    }
  }

  if (testintable) {

    AMObj headfun;
    amobjTable()->findValue(fname, headfun);

    if (headfun.tag != AMObjType::FNODE) {
      genAMLError(ERRORMSG(K_ITER_ARG_TYPE_ERR_sdss), "Foreach", 1, headfun.tag.string().data(), "syntactically a function");
      retval = new FAMObj(AMObj(AMObjType::ERROR));
      return retval;
    }
    assert(headfun.val.p);

    FNode* fun = ((FNode*) headfun.val.p);

    // make the union of all free variables
    StringList* varlist = makeFreeVarList(&list);

    // ------------------
    // Recursive function
    // ------------------

    if (!fun->isValid()) { // the function is being defined recursively

      if (varlist->isEmpty()) { // the current FExp does not contain any variable so it can be evaluated

        AMLCOMMENT("Recursive definition : cannot evaluate the function during its definition ... ");

        delete varlist;

        retval =  new FAMObj(AMObj(AMObjType::ERROR));

      }
      else {

        FNode* recfun = new FNode("", fun, varlist, &list);
        //assert(recfun->isValid());

        retval =  new FAMObj(AMObj(AMObjType::FNODE, recfun), varlist);

      }

    }
    else { // Non recursive definition

      int nbargs = list.entries();

      if (varlist->isEmpty()) { // the current FExp does not contain any variable so it can be evaluated

        // ----------------------------------
        // Non Recursive Evaluable Expression
        // ----------------------------------

        if (testintable == 1) { // In case of a user function, one has to check the correctness of the number of args
          if (fun->argNb() != nbargs) {
            genAMLError(ERRORMSG(ARGLIST_NB_ERR_sd), fname.data(), nbargs);
            delete varlist;
            retval = new FAMObj(AMObj(AMObjType::ERROR));
            return retval;
          }
        }

        AMObjVector argobjs;            // construct a vector of length 0

        if (nbargs) argobjs.reshape(nbargs);    // AMObjVector argobjs(0) is not a valid statement

        for (register int i=0; i<nbargs; i++) {
          argobjs[i] = *(list[i]);      // AMObj = FAMObj !
        }

        // call the function
        AMObj eval = (*fun)(argobjs);   // create an object which must be cleared and destroyed

        retval = new FAMObj(eval, varlist);

      }
      else {

        // ----------------------
        // Non Recursive function
        // ----------------------

        if (testintable == 1) { // In case of a user function, one has to check the correctness of the number of args
          if (fun->argNb() != nbargs) {
            genAMLError(ERRORMSG(ARGLIST_NB_ERR_sd), fname.data(), nbargs);
            delete varlist;
            retval = new FAMObj(AMObj(AMObjType::ERROR));
            return retval;
          }
        }

        FNode* fnode = new FNode("", fun, varlist, &list);

        if (!fnode->isValid()) {  // failed for example because an argument is a function

          retval = new FAMObj(AMObj(AMObjType::ERROR));

        }

        retval =  new FAMObj(AMObj(AMObjType::FNODE, fnode), varlist);

      }

    }

  }
  else { // name not in the symbol Table

    AMLOUTPUT << std::endl << "Function \"" << fname << "\" does not exists." << std::endl;

    retval = new FAMObj(AMObj(AMObjType::ERROR));

  }

  return retval;

}


static FAMObj* iter_eval(RWCString fname, const FAMObjPtrList& list, RWCString tiedvar) {

  FAMObj* retval;

  // If there exists an error in the argument list abort here
  if (!(checkIterEvalArgListValidity(list))) {

    return new FAMObj(AMObj(AMObjType::ERROR));

  }

  if (amobjTable()->contains(fname)) { // fname is the name of an iterator

    AMObj headiter;
    amobjTable()->findValue(fname, headiter);

    assert(headiter.tag == AMObjType::FNODE);
    assert(headiter.val.p);

    FNode* iter = ((FNode*) headiter.val.p);

    // make the union of all free variables
    StringList* varlist = makeFreeVarList(&list);
    assert(varlist);

    // the tied variable might exists in the freevarlist => remove it
    varlist->remove(tiedvar);

    if (varlist->isEmpty()) { // the current FExp does not contain any variable so it can be evaluated

      assert(list.entries() == 2);

      AMObjVector argobjs(list.entries());

      for (register int i=0; i<list.entries(); i++) {
        argobjs[i] = *(list[i]); // AMObj = FAMObj !
      }

      FNode* fniter = new FNode("", iter, varlist, tiedvar, &list);

      // call the iterator
      AMObj eval = (*fniter)(argobjs);

      delete fniter;

      retval = new FAMObj(eval, varlist);

    }
    else {

      FNode* fniter = new FNode("", iter, varlist, tiedvar, &list);
      assert(fniter->isValid());

      retval =  new FAMObj(AMObj(AMObjType::FNODE, fniter), varlist);

    }

  }
  else { // name not in the symbol Table

    assert(FALSE);

  }

  return retval;

}

static StringList* makeFreeVarList(const FAMObjPtrList* objlist) {

  assert(objlist);
  FAMObjPtrListIter next(*(FAMObjPtrList*)objlist);

  StringList* varlist = new StringList;

  while (next()) {

    FAMObj* famobj = next.key();

    // AMLOUTPUT << *famobj << endl;

    switch(famobj->tag.type) {
    case AMObjType::VAR:
      if (!varlist->contains(*(AMString*)(famobj->val.p))) varlist->insert(*(AMString*)(famobj->val.p));
      break;
    case AMObjType::FNODE:
      {
        // add the list of arg string of this FNode to var list;
        if (famobj->arglist) { // fAMObjVector can be 0 for e.g. in   '? fun'
          StringListIter nextvar(*famobj->arglist);
          while(nextvar()) {
            RWCString varstg = nextvar.key();
            if (!varlist->contains(varstg)) varlist->insert(varstg);
          }
        }
      }
      break;
    default:
      break;
    }

  }

  return varlist;

}

// list1 consists of names such as (_x, _y, _z, _w) indexed from 0 to m-1
// list2 consists of names such as (_y, _x, _w) indexed from 0 to n-1
//
// we must have n <= m and every element in list2 should be in list1
// also int should have enough space (at least n)
//
// the result is a mapping from list2 into list1:
// in the above example this consists of an array of int's, ranging from 0 to m-1, of size n:
// ex: result = [1,0,3]
//
// if a requirement is not met, a boolean False is returned
//

static AmlBoolean matchVarLists(const StringList* list1, const StringList* list2, int* result) {

  assert(list1);
  assert(list2);

  int m = list1->entries();
  int n = list2->entries();

  if (n > m) return FALSE;

  StringListIter next2(*(StringList*) list2);

  int i = 0;

  while (next2()) {

    result[i] = list1->index(next2.key());
    if (result[i] == RW_NPOS) return FALSE;
    i++;

  }

  return TRUE;

}


// -----------------
// Parser management
// -----------------

#include "tool/util_enviro.h"

static void initLogFile() {

  if (log_file) log_file->close();
  delete log_file;
#ifdef _WIN32
  char * rootdir = getenv("AMAPMOD_DIR");
  RWCString log_f;
  if(!rootdir)  log_f = LOG_FILE;
  else  {
        log_f = rootdir ;
        log_f += '\\';
    log_f += LOG_FILE;
  }
  log_file = new std::ofstream(log_f.data());
#else
  log_file = new std::ofstream(LOG_FILE);
#endif

  if (!(*log_file)) {
    AMLOUTPUT << "Cannot open file for writing : "
    << LOG_FILE << std::endl;
    delete log_file;
    log_file = 0;
  }

  if (log_file) {

    *log_file << "# shell : aml " << std::endl;
    *log_file << "#----------------------------------------------------------------#" << std::endl;
    *log_file << "# LOG FILE : " << __DATE__ << " created by " << VPTOOLS(getUserName()).c_str() << std::endl;
    *log_file << "# File Generated by AMAPmod " << release_number() << " on "<< VPTOOLS(getOSName()).c_str() << std::endl;
    *log_file << "#----------------------------------------------------------------#" << std::endl;
    *log_file << "#" << std::endl << std::endl;

  }

}

void initParser(std::ostream* stream) {

  errlist = new AMLErrorList;

  if(!stream)
    {
#ifdef QT_AML
    aml_output_stream =qtOuput();
#else
    aml_output_stream = &std::cout;
#endif
    }
  else
    {
    aml_output_stream = stream;
    }
  initLogFile();

}


void cleanParser() {

  delete errlist;
  errlist = 0;

  if (input_stream) input_stream->close();
  delete input_stream;
  input_stream = 0;

  // Cleaning for Gnuplot Interface
  char buffer[100];
#ifdef _WIN32
  if(VPTOOLS(exists)(string(Plot_prefix)+string(".plot"))){
	string cmd = string("ERASE /F /Q ") + Plot_prefix + "*";
    if (system(cmd.c_str()) == -1) {
        aml_system_error(AMLOUTPUT , "ERASE");
    }
  }
#else
#ifndef STL_EXTENSION
  std::ostrstream(buffer, 100) << "rm -f " << Plot_prefix << "*" << std::ends;
  if (system(buffer) == -1) {
    aml_system_error(AMLOUTPUT , "rm -f");
  }
#else
  std::ostringstream os;
  os<< "rm -f " << Plot_prefix << "*" << std::ends;
  if (system(os.str().c_str()) == -1) {
    aml_system_error(AMLOUTPUT , "rm -f");
  }

#endif
#endif

  if (log_file) log_file->close();
  delete log_file;
  log_file = 0;

}

static int getNextLine() {

  errlist->clear(); // each new line the set of errors is cleared

  if (AMLGetNextLine(input_buff)) { // returns the user's string including the terminating '\n' in input_buff

    amlPointOnInputBuffer(input_buff); // to make lex point on buff as input

    return TRUE;

  }
  else {
    return FALSE;
  }

}

// ----------------
// extern functions
// ----------------

#define MAX_INCLUDE_DEPTH 20
struct strFile {
	string file;
	string dir;
	istream * stream;
	bool inc;

};

static stack<struct strFile> __inputstream;
static stack<AMObjVector> __streamarg;

static stack<queue<AMObjVector> >__streamqueue;
static bool in_enqueue = false;
static int in_include = 0;
static string c_file;
static bool in_inc = false;

bool isInputCin(){
	return AMLGetNextLine == readline_interactive;
}

static bool IncludeToDo(){
//	if(!in_include) return false;
	if(__streamqueue.empty()) return false;
	if(in_include < __streamqueue.size()){
		return true;
	}
	return false ;
}

bool pushInclude(const AMObjVector& v) {
	if(!in_enqueue){
		__streamqueue.push(queue<AMObjVector>());
	}
	__streamqueue.top().push(v);
	in_enqueue = true;
	return true;
}
bool push_File(const char* file,bool inc);
bool pushFile(const char* file){
	return push_File(file,false);
}

static bool EvalInclude() {
  if(!IncludeToDo())return false;
  if(__streamqueue.empty())return false;
  AMObjVector args = __streamqueue.top().front();
  __streamqueue.top().pop();
  for(int i = 1; i < args.length(); i++){
	RWCString str(*(AMString*)(args[i].val.p));
	amobjTable()->insert(str,args[i+1]);i++;
  }

  RWCString str(*(AMString*)(args[0].val.p));
  push_File(str.data(),true);
  return true;
}

bool push_File(const char* file,bool inc = false){
  if(__inputstream.size() >= MAX_INCLUDE_DEPTH){
	AMLOUTPUT << "MAX_INCLUDE_DEPTH reached. Cannot include more." << endl;
	return false;
  }
  ifstream * _input_stream = new ifstream(file);
  if(!_input_stream){
	AMLOUTPUT << "Cannot include file " << file << endl;
	return false;
  }

  string new_cwd = VPTOOLS(get_dirname)(file);     // gets the new working dir name
  string _cwd = get_cwd();
  if (new_cwd != "") {                // defines the new cwd
	if (!chg_dir(new_cwd)) AMLOUTPUT << "\tchg_dir() returned an error." << endl;
  }

  if (input_stream)	{
	struct strFile f;
	f.file = c_file;
	f.dir = _cwd;
	f.stream = input_stream;
	f.inc=in_inc;
	__inputstream.push(f);
  }
  else if(isInputCin()){
	struct strFile f;
	f.file = "cin";
	f.dir = "";
	f.stream = &cin;
	f.inc=in_inc;
	__inputstream.push(f);
	initGetNextLineFunc(readline_file);
  }
  in_inc = inc;
  if(in_inc)in_include++;
  input_stream = _input_stream;
  c_file = file;
 // cout << "Beg Include : " << in_include << "->" << __inputstream.size() <<":"<<c_file << endl;
//  AMLOUTPUT << "Include \"" << file << " " << in_include << '-' << __inputstream.size() << endl;
  return true;
}

bool popStream(){
//	cerr << "popStream : " << __inputstream.size() << endl;
 //   cout << endl << "End Include : " << __streamqueue.size() << "->" << in_include <<":"<<c_file <<  endl;
	if(in_inc){
		in_include--;
		if(__streamqueue.top().empty()){
			__streamqueue.pop();
		}
	}
	if(__inputstream.empty()){
		c_file = "cin";
		return false;
	}
	struct strFile p = __inputstream.top();
	__inputstream.pop();
	istream * _input_stream = p.stream;
	string _cwd = p.dir;
	c_file = p.file;
	in_inc = p.inc;
	if (_cwd != "") {                // defines the new cwd
		if (!chg_dir(_cwd)) AMLOUTPUT << "\tchg_dir() returned an error." << endl;
	}


	if(_input_stream == &cin){
		initGetNextLineFunc(readline_interactive);
		input_stream = NULL;
	}
	else {
		delete input_stream;
		input_stream = (ifstream *)_input_stream;
	}
	return true;
}

void initGetNextLineFunc(NextLineFunc pf) {
  assert(pf);
  AMLGetNextLine = pf;

}

// Getting next line to parse from a file
int file_init_read_line(const char* file) {
	return pushFile(file);
/*
  if (input_stream) input_stream->close();
  delete input_stream;
  input_stream = new std::ifstream(file);

  if (!(*input_stream)) {
    AMLOUTPUT << "Cannot open file for reading : "
    << file << std::endl;
    delete input_stream;
    input_stream = 0;
    return 0;
  }
  else return 1;
*/
}


#ifdef QT_AML
#define cinInputLine qtInputLine
#else
bool cinInputLine(char * buff, int maxlength){
    std::cin.getline(buff,maxlength);
    if (std::cin.fail()) return false;
        else return true;
}
#endif

int readline_interactive(char* buff) {
  in_enqueue = false;
  if(IncludeToDo())return readline_file(buff);

#ifdef USE_READLINE
  int r, pos;

  RWCString tmp;
  RWCString result;

  do {

    input_buff[0] = '\n'; // to flush at each new line the old buffer
    input_buff[1] = '\0'; // this line is absolutely required

    r = readline_input(buff);

    if (r) {

      if (log_file)
      *log_file << buff << std::flush;

      tmp = buff;

      pos = tmp.last('\\');

      int flag = FALSE;

      if (pos != RW_NPOS) {
        for (register int i = pos+1; i<tmp.length() && tmp(i) != '\n'; i++)
        if (tmp(i) != ' ' && tmp(i) != '\t') {
          flag = TRUE;
          break;
        }
        if (!flag) tmp.remove(pos);
      }

      result += tmp;

      if (flag) break;

    }
    else break;

  }
  while (pos != RW_NPOS);

  //cerr << "Expression lue = " << result << endl;

  if (result.length() >= MAXLINELENGTH) {

    AMLOUTPUT << "Warning : Expression too long !" << std::endl;

  }
  strncpy(buff, result.data(), MAXLINELENGTH);

  return r;
#else
  int pos;
  // '\n' is left in the input and should be added to buff
  // return a string of characters finished by \0
  RWCString tmp;
  RWCString result;

  do {
#ifndef QT_AML
    std::cout << "AML> " << std::flush;
#endif

    input_buff[0] = '\n'; // to flush at each new line the old buffer
    input_buff[1] = '\0'; // this line is absolutely required

    if (!cinInputLine(buff,MAXLINELENGTH+1)) return 0;
    else {

      if (log_file)
      *log_file << buff << std::endl;

      tmp = buff;

      if (buff[0] == '(' && buff[1] == '#') {

        do {

          if (!cinInputLine(buff,MAXLINELENGTH+1)) return 0;
          tmp = buff;


        } while (buff[0] != '#' || buff[1] != ')') ;

      }


      pos = tmp.last('\\');

      int flag = FALSE;

      if (pos != RW_NPOS) {
        for (register int i = pos+1; i<tmp.length() && tmp(i) != '\n'; i++)
        if (tmp(i) != ' ' && tmp(i) != '\t') {
          flag = TRUE;
          break;
        }
        if (!flag) tmp.remove(pos);
      }

      result += tmp;

      if (flag) break;

    }

  }
  while (pos != RW_NPOS);

  // The read string from the file is in result.

  if (result.length() >= MAXLINELENGTH) {

    AMLOUTPUT << "Warning : Expression too long !" << std::endl;

  }
  strncpy(buff, result.data(), MAXLINELENGTH);

  int l = strlen(buff);
  assert(l<MAXLINELENGTH-1);

  buff[l] = '\n'; // instead of \0
  buff[l+1] = '\0'; // instead of \0

  return 1;

#endif

}

// Getting next line to parse interactively from readline
int readline_file(char* buff) {
  in_enqueue = false;
  EvalInclude();

  int pos;
  // '\n' is left in the input and should be added to buff
  // return a string of characters finished by \0
  RWCString tmp;
  RWCString result;

  do {

    input_buff[0] = '\n'; // to flush at each new line the old buffer
    input_buff[1] = '\0'; // this line is absolutely required

    input_stream->getline(buff,MAXLINELENGTH+1);

    if (input_stream->fail()){
		if(!popStream())return 0;
		else {
			input_buff[0] = '\n';
			input_buff[1] = '\0';
			return 1;
		}
	}
    {

      tmp = buff;

      if (buff[0] == '(' && buff[1] == '#') {

        do {

          input_stream->getline(buff,MAXLINELENGTH+1);
          if (input_stream->fail()) return 0;
          tmp = buff;


        } while (buff[0] != '#' || buff[1] != ')') ;

      }

      //cerr << "tmp = " << tmp << endl;

      pos = tmp.last('\\');

      int flag = FALSE;

      if (pos != RW_NPOS) {
        for (register int i = pos+1; i<tmp.length() && tmp(i) != '\n'; i++)
        if (tmp(i) != ' ' && tmp(i) != '\t') {
          flag = TRUE;
          break;
        }
        if (!flag) tmp.remove(pos);
      }

      result += tmp;

      if (flag) break;

    }

  }
  while (pos != RW_NPOS);

  // The read string from the file is in result.

  if (result.length() >= MAXLINELENGTH) {

    AMLOUTPUT << "Warning : Expression too long !" << std::endl;

  }
  strncpy(buff, result.data(), MAXLINELENGTH);

  int l = strlen(buff);
  assert(l<MAXLINELENGTH-1);

  buff[l] = '\n'; // instead of \0
  buff[l+1] = '\0'; // instead of \0

  return 1;

}


void amlEchoOn() {

  AMLECHO = TRUE;

}

void amlEchoOff() {

  AMLECHO = FALSE;

}


std::ostream& getAMLOutputStream() {

  assert(aml_output_stream);
  return *aml_output_stream;

}


AMLErrorList* getAMLErrorList() {

  return errlist;

}

static AmlBoolean anyErrors() {

  assert(errlist);

  return errlist->entries();

}

static void printErrorList() {

  assert(errlist);

  AMLErrorItemListIter next(*errlist);

  while(next()) {

    next.key().print(AMLOUTPUT);
    AMLOUTPUT << std::endl;

  }

  errlist->clear();

}

// creates a new error item containing at least:
// - the type of the error
// - the line and column number of the error
// - the state of the current line when the error occurs

int yyerror(char* errtype) {

  assert(errtype);

  errlist->insert(AMLErrorItem(errtype,
                               yychar,
                               amlCurrentLine(),
                               input_buff
                               )
                  );

  /*
     std::cerr << std::endl << "YYERROR:" << s << ": TOKEN = " << yychar << " , \"" << amlText() << "\"" <<  std::endl;
     std::cerr << "input line = \"" << amlCurrentLine() << "\"" << std::endl;
     std::cerr << "line = " << input_buff << std::endl;
  */

  return 1;

}


const char* amlTokenName(int token) {

  static char tmp[2];

  assert(token <= TokError);

  if (token >= TokSystemCall) return token_name[token-TokSystemCall];
  else if (token == YYEOF) return "EOF";
  else if (token == YYEMPTY) return "VOID";
  else {
    tmp[0] = token;
    tmp[1] = 0;
    return tmp;
  }

}
