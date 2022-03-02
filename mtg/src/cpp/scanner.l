%{ //-*-c++-*-
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
 *       $Id: scanner.l 3263 2007-06-06 14:07:06Z dufourko $
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




#include <iostream>
#include <string>
#ifdef SYSTEM_IS__IRIX
#include <values.h>
#else
#include <float.h>
#define MINFLOAT FLT_MIN
#define MAXFLOAT FLT_MAX
#endif
#include "tool/config.h"

#include "aml/defs.h"

#include "parser_dec.h"
#ifdef BISON_HPP
#include "parser.hpp"
#else
#include "parser.cpp.h"
#endif

static const char rcsid[] = "$Id: scanner.l 3263 2007-06-06 14:07:06Z dufourko $";

#ifdef _WIN32
extern "C" {
  int isatty (int handle);
}

#define YY_SKIP_YYWRAP
int yywrap() {
  return 1;
}

#endif

#if 0

#define SCANNERDEBUG

#if 1
#define SIMPIFIEDSCANNERDEBUG
#endif

#endif

#ifdef SCANNERDEBUG
#define STATE(x)
#else
#define STATE(x)
#endif


#ifdef SCANNERDEBUG

#ifndef SIMPIFIEDSCANNERDEBUG

static void TraceTok(char* s, char* t) {

  if (s[0] == '\n') std::cerr << "[eol<" << t << ">]" << std::flush;
  else std::cerr << "[" << s << "<" << t << ">]" << std::flush;

  if (strcmp(s,"eol") == 0) std::cerr << std::endl;
  else if (strcmp(s,"wln") == 0) std::cerr << std::endl;

}

#else

static void TraceTok(char* s) {

  if (s[0] == '\n') std::cerr << "[eol]" << std::flush;
  else std::cerr << "[" << s << "]" << std::flush;

  if (strcmp(s,"eol") == 0) std::cerr << std::endl;
  else if (strcmp(s,"wln") == 0) std::cerr << std::endl;

}

#endif

static void Trace(char* s) {

  std::cerr << "(" << s << ")" << std::flush;

  if (strcmp(s,"eol") == 0) std::cerr << std::endl;
  else if (strcmp(s,"wln") == 0) std::cerr << std::endl;

}

#ifndef SIMPIFIEDSCANNERDEBUG
static void PrintLineNb() {
  std::cerr << "\nLINENB " << linenb << " :"<< std::endl;
}
#else
#define PrintLineNb()
#endif

#else

#ifdef SIMPIFIEDSCANNERDEBUG
#define TraceTok(s)
#else
#define TraceTok(s,t)
#endif

#define Trace(s)
#define PrintLineNb()

#endif

#ifdef SIMPIFIEDSCANNERDEBUG
#define TRACE(t) cat_curr_line_buf();TraceTok(yytext)
#else
#define TRACE(t) cat_curr_line_buf();TraceTok(yytext, t)
#endif

static int linenb = 1;
static int colnb = 1;
static int previous_colnb = 1;

static int previous_state = YY_START;

static char curr_line_buf[MAXLINELENGTH] = {'\0'};
static char prev_line_buf[MAXLINELENGTH] = {'\0'};

static void cat_curr_line_buf();
static void reset_curr_line_buf();

static MTGCode mtg_code;

#define YY_USER_ACTION  previous_state = YY_START; // current state of the scanner

%}


INT     [0-9]+
WSC     [ \0]
LN      \n
TAB     \t
CHAR    [A-Za-z]
NAME    [A-Za-z_][A-Za-z_0-9\-]*
STG     [A-Za-z_0-9 \-/\.\+]+
COMMENT #[^\t\n]*
FLNM    [^ \t\n#]+
%s START FILENAME CODE_A CODE_B MTGFEATURE


%%

<START,FILENAME,CODE_A,CODE_B,MTGFEATURE>^({WSC}|{TAB}|{COMMENT})*\n    {Trace("wln");reset_curr_line_buf();linenb++;colnb=1;PrintLineNb();}
<START,FILENAME,CODE_A,CODE_B,MTGFEATURE>{WSC}+         {Trace("wsc");cat_curr_line_buf();}
<START,FILENAME,CODE_A,CODE_B,MTGFEATURE>{COMMENT}      {Trace("comment");}

<START>CODE             {TRACE("TokCODE"); return(TokCODE);}
<START>FORM-A           {TRACE("TokFORM_A"); mtg_code = FORM_A; return(TokFORM_A);}
<START>FORM-B           {TRACE("TokFORM_B"); mtg_code = FORM_B; return(TokFORM_B);}

<START>CLASSES          {TRACE("TokCLASSES"); return(TokCLASSES);}
<START>SYMBOL           {TRACE("TokSYMBOL"); return(TokSYMBOL);}
<START>SCALE            {TRACE("TokSCALE"); return(TokSCALE);}
<START>DECOMPOSITION    {TRACE("TokVDECOMP"); return(TokVDECOMP);}
<START>INDEXATION       {TRACE("TokINDEXATION"); return(TokINDEXATION);}
<START>DEFINITION       {TRACE("TokVDEF"); return(TokVDEF);}
<START>LINEAR           {TRACE("TokLINEAR"); yylval.intval = LINEAR; return(TokInteger);}
<START>"<-LINEAR"       {TRACE("TokLESSLINEAR"); yylval.intval = LESSLINEAR; return(TokInteger);}
<START>"+-LINEAR"       {TRACE("TokPLUSLINEAR"); yylval.intval = PLUSLINEAR; return(TokInteger);}
<START>PURELINEAR           {TRACE("TokPURELINEAR"); yylval.intval = PURELINEAR; return(TokInteger);}
<START>"<-PURELINEAR"       {TRACE("TokLESSPURELINEAR"); yylval.intval = LESSPURELINEAR; return(TokInteger);}
<START>"+-PURELINEAR"       {TRACE("TokPLUSPURELINEAR"); yylval.intval = PLUSPURELINEAR; return(TokInteger);}
<START>CONNECTED        {TRACE("TokCONNECTED"); yylval.intval = CONNECTED; return(TokInteger);}
<START>NOTCONNECTED     {TRACE("TokNOTCONNECTED"); yylval.intval = NOTCONNECTED; return(TokInteger);}
<START>FREE             {TRACE("TokFREE"); yylval.intval = FREE_D; return(TokInteger);}
<START>NONE             {TRACE("TokNONE"); yylval.intval = NONE_D; return(TokInteger);}
<START>CONSECUTIVE      {TRACE("TokCONSECUTIVE"); yylval.intval = CONSECUTIVE; return(TokInteger);}
<START>EXPLICIT         {TRACE("TokEXPLICIT"); yylval.intval = EXPLICIT; return(TokInteger);}
<START>IMPLICIT         {TRACE("TokIMPLICIT"); yylval.intval = IMPLICIT; return(TokInteger);}

<START>DESCRIPTION      {TRACE("TokDESCRIPTION"); return(TokDESCRIPTION);}
<START>LEFT             {TRACE("TokLEFT"); return(TokLEFT);}
<START>RIGHT            {TRACE("TokRIGHT"); return(TokRIGHT);}
<START>RELTYPE          {TRACE("TokRELTYPE"); return(TokRELTYPE);}
<START>MAX              {TRACE("TokMAX"); return(TokMAX);}
<START>"?"              {TRACE("TokInteger"); yylval.intval = MAXINT; return(TokInteger);}
<START>","              {TRACE(","); return(',');}

<START>FEATURES         {TRACE("TokFEATURES"); return(TokFEATURES);}
<START>NAME             {TRACE("TokFNAME"); return(TokFNAME);}
<START>TYPE             {TRACE("TokFTYPE"); return(TokFTYPE);}
<START>INT              {TRACE("TokFType"); yylval.ftypeval = INTEGER; return(TokFType);}
<START>ALPHA            {TRACE("TokFType"); yylval.ftypeval = ALPHA; return(TokFType);}
<START>STRING           {TRACE("TokFType"); yylval.ftypeval = ALPHA; return(TokFType);}
<START>REAL             {TRACE("TokFType"); yylval.ftypeval = REAL; return(TokFType);}
<START>"DD/MM"          {TRACE("TokFType"); yylval.ftypeval = DDMM; return(TokFType);}
<START>"DD/MM/YY"       {TRACE("TokFType"); yylval.ftypeval = DDMMYY; return(TokFType);}
<START>"MM/YY"          {TRACE("TokFType"); yylval.ftypeval = MMYY; return(TokFType);}
<START>"DD/MM-TIME"     {TRACE("TokFType"); yylval.ftypeval = DDMMTIME; return(TokFType);}
<START>"DD/MM/YY-TIME"  {TRACE("TokFType"); yylval.ftypeval = DDMMYYTIME; return(TokFType);}

<START>GEOMETRY         {TRACE("TokFType"); BEGIN FILENAME; yylval.ftypeval = GEOMETRY; return(TokFType);}
<START>APPEARANCE       {TRACE("TokFType"); BEGIN FILENAME; yylval.ftypeval = APPEARANCE; return(TokFType);}
<START>SHAPE            {TRACE("TokFType"); BEGIN FILENAME; yylval.ftypeval = GENERIC; return(TokFType);}

<FILENAME>{FLNM}        {TRACE("TokFilename"); BEGIN START; sprintf(yylval.stgval,"%s",yytext); return(TokFilename);}

<START>Date             {TRACE("TokDate"); sprintf(yylval.stgval,"%s",yytext); return(TokString);}
<START>NbEl             {TRACE("TokNbEl"); sprintf(yylval.stgval,"%s",yytext); return(TokString);}
<START>Length           {TRACE("TokLength"); sprintf(yylval.stgval,"%s",yytext); return(TokString);}
<START>Diam             {TRACE("TokDiam"); sprintf(yylval.stgval,"%s",yytext); return(TokString);}
<START>State            {TRACE("TokState"); sprintf(yylval.stgval,"%s",yytext); return(TokString);}

<START>MTG              {TRACE("TokMTG"); return(TokMTG);}
<START>ENTITY-CODE      {TRACE("TokENTITYCODE"); return(TokENTITYCODE);}
<START>TOPO             {TRACE("TokENTITYCODE"); return(TokENTITYCODE);}

<START,CODE_A,CODE_B>":"        {TRACE(":"); return(':');}
<START>{LN}     {TRACE("eol");linenb++;previous_colnb = colnb; colnb=1;reset_curr_line_buf();PrintLineNb();return eol;}
<CODE_A,CODE_B,MTGFEATURE>{LN}          {TRACE("eol");linenb++;previous_colnb = colnb; colnb=1;reset_curr_line_buf();PrintLineNb(); startCodeState();return eol;}
<START,FILENAME>{TAB}           {TRACE("tab");previous_colnb = colnb; colnb++;return tabc;}
<CODE_A,CODE_B,MTGFEATURE>{TAB}         {TRACE("tab");previous_colnb = colnb; colnb++; if (colnb>=firstFeatCol() && firstFeatCol() != -1) startFeatureState();return tabc;}
<START,CODE_A,CODE_B>"+"        {TRACE("TokReltype"); yylval.etypeval = &PLUS; return(TokReltype);}
<CODE_A,CODE_B>"/"      {TRACE("TokReltype"); yylval.etypeval = &SLASH; return(TokReltype);}
<START,CODE_A>"<"       {TRACE("TokReltype"); yylval.etypeval = &LESS; return(TokReltype);}
<START,CODE_A>"<<"      {TRACE("TokReltype"); yylval.etypeval = &LESSLESS; return(TokReltype);}
<START,CODE_A>"++"      {TRACE("TokReltype"); yylval.etypeval = &PLUSPLUS; return(TokReltype);}
<START,CODE_A>"<.<"     {TRACE("TokReltype"); yylval.etypeval = &LESSDOTLESS; return(TokReltype);}
<START,CODE_A>"+.+"     {TRACE("TokReltype"); yylval.etypeval = &PLUSDOTPLUS; return(TokReltype);}
<START>{CHAR}|\$        {TRACE("TokSymbol"); yylval.charval = yytext[0]; return TokSymbol;}

<CODE_A,CODE_B>"("      {TRACE("("); startFeatureState(); return('(');}
<MTGFEATURE>")"         {TRACE(")"); startCodeState(); return(')');}
<CODE_A,CODE_B>"^"      {TRACE("^"); return('^');}
<CODE_A,CODE_B>"*"      {TRACE("*"); return('*');}
<CODE_A,CODE_B>{CHAR}   {TRACE("TokSymbol"); yylval.charval = yytext[0]; return TokSymbol;}
<START,CODE_A,CODE_B>{INT}      {TRACE("TokInteger"); yylval.intval = atoi(yytext); return(TokInteger);}

<START>{NAME}           {TRACE("TokString"); sprintf(yylval.stgval,"%s",yytext); return(TokString);}
<MTGFEATURE>{STG}       {TRACE("TokString"); sprintf(yylval.stgval,"%s",yytext); return(TokString);}
<CODE_A,CODE_B,MTGFEATURE><<EOF>>       {/*cerr << "<<EOF>>" << std::endl;*/ yyterminate();}

<START,FILENAME,CODE_A,CODE_B,MTGFEATURE>.      {TRACE("ReadError");return TokError;}

%%

void startStartState() {

#ifdef SCANNERDEBUG
  std::cerr << "{START}";
#endif

  BEGIN START;

}

void startFeatureState() {

#ifdef SCANNERDEBUG
  std::cerr << "{FEATURE}";
#endif

  BEGIN MTGFEATURE;

}

void startCodeState() {

  switch(mtg_code) {
  case FORM_A:
    BEGIN CODE_A;
#ifdef SCANNERDEBUG
    std::cerr << "{CODE_A}";
#endif
    break;
  case FORM_B:
    BEGIN CODE_B;
#ifdef SCANNERDEBUG
    std::cerr << "{CODE_B}";
#endif
    break;
  }

}

const char* yyText() {

  return yytext;

}

int yyLineNb() {

  return linenb;

}

int yyColumnNb() {

  return colnb;

}

int yyPreviousColumnNb() {

  return previous_colnb;

}

const char* yyCurrentLine() {

  return curr_line_buf;

}

const char* yyPreviousLine() {

  return prev_line_buf;

}

int yyTokenLength() {

  return yyleng;

}

static void cat_curr_line_buf() {

  if (yytext[0] != '\n')
  if (strlen(curr_line_buf) + strlen(yytext) < MAXLINELENGTH) strcat(curr_line_buf, yytext);
}

static void reset_curr_line_buf() {

  //  cerr << "line# " << yyLineNb()-1 << ":\t" << curr_line_buf << endl;

  strcpy(prev_line_buf, curr_line_buf);
  curr_line_buf[0] = '\0';

}

static void lexunput(char c) {

  // after unputting a '\n' the prev_line_buf is nolonger OK
  // should not be used
  if (c == '\n')  {
#ifdef SCANNERDEBUG
    fprintf(stderr,"<^\\n>");
#endif
    strcpy(curr_line_buf, prev_line_buf);
  }
  if (c == '\t')  {
#ifdef SCANNERDEBUG
    fprintf(stderr,"<^\t>");
#endif
    if (strlen(curr_line_buf)) {curr_line_buf[strlen(curr_line_buf)-1] = '\0';}
  }
  else {
#ifdef SCANNERDEBUG
    fprintf(stderr,"<^%c>", curr_line_buf[strlen(curr_line_buf)-1]);
#endif
    if (strlen(curr_line_buf)) {curr_line_buf[strlen(curr_line_buf)-1] = '\0';}
  }

  unput(c);
}

/* La fonction unput(char c) ne gere pas un index sur le fichier ouvert
   mais tamponne les caracteres recu dans un buffer special 'yysbuf'.
   Ceci permet de faire unput(c) sur des carcateres n'appartenant pas
   au fichier original; input tient compte de ce buffer pour sortir
   des caracteres.

*/

void yyUnputToken() {

  register int i;
  for(i=yyleng-1;i>=0;i--) lexunput(yytext[i]);

  // recover the scanner state before analysing this token

  switch(previous_state) {

  case START:
    startStartState();
    break;
  case CODE_A:
  case CODE_B:
    startCodeState();
    break;
  case MTGFEATURE:
    startFeatureState();
    break;

  }

}

/* Lex ATT ne sait pas se reinitialiser tout seul */

void lexAbort() {

  startStartState();

  yyrestart(yyin); // In case the parser abort while the scanner still proceeds

  linenb = 1;
  colnb = 1;

}



