%{
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
 *       $Id: scanneraml.l 3262 2007-06-06 13:53:44Z dufourko $
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
#include <assert.h>
#include <stdlib.h>

#include "tool/config.h"

#include "scanneraml.h"
#include "parseraml.h"

#ifdef BISON_HPP
#include "parseraml.hpp"
#else
#include "parseraml.cpp.h"
#endif

#if 0
#define LEXDEBUG
#endif

#ifdef _WIN32
extern "C" {
  int isatty (int handle);
}
#endif

#define TRACE cat_curr_line_buf();Trace(yytext)
static char curr_line_buf[MAXLINELENGTH] = {'\0'};
static char prev_line_buf[MAXLINELENGTH] = {'\0'};

static void cat_curr_line_buf();
static void reset_curr_line_buf();

// Redefine YY_INPUT to use a string as an input to flex
#undef YY_INPUT
#define YY_INPUT(yybuff,res,max)        (res = getyyinput(yybuff,max))

void Trace(char*);

static const char* string_buff = 0;


// In general, maxsize is small (corresponds to a block of characteres
// read simultaneously). Then the scanner must call YY_INPUT several
// times to reach the end of the input.
// We oblige maxsize = 1 so that the procedure YY_INPUT for each
// character : no buffering is done which enables to read correctly
// a newly installed string whenever a parsing error occur.

static int getyyinput(char* yybuff, int maxsize) {

  assert(string_buff);
  assert(yybuff);

  maxsize = 1;
  int len = std::min((int)strlen(string_buff)+1, maxsize);

  // cerr << "len = " << len << endl;

  if (len > 0) {
    memcpy(yybuff, string_buff, len);
    string_buff += len;
  }

  return len;

}


/*
int swallow_comment() {

  register int c;

  while (1) {

    while ( (c = yyinput()) != '#' && c != EOF) ;

    if (c == '#')  {

      while ( (c = yyinput()) == '#') ;

      if (c == ')') break;

    }

    if (c == EOF) {

       std::cerr << "EOF in comment";
       break;

    }

  }

  return 1;

}
*/


%}



S       [a-zA-Z_]([0-9]|[a-zA-Z_])*
B       [ \t]+
N       (#.*)*\n
D       [0-9]+
R       ({D}"."{D}?)|({D}?"."{D})|({D}("."{D}?)?[Ee][+-]?{D})|("."{D}[Ee][+-]?{D})


%%



^{B}*Quit	{TRACE;if(!popStream()) yyterminate();}
^{B}*quit	{TRACE;if(!popStream()) yyterminate();}
^{B}*Exit	{TRACE;if(!popStream()) yyterminate();}
^{B}*exit	{TRACE;if(!popStream()) yyterminate();}
^{B}*bye	{TRACE;if(!popStream()) yyterminate();}

!([^=].*)?$	{TRACE; 
                 amllval.String = new char[strlen(yytext)]; 
                 strcpy(amllval.String,yytext+1); 
                 return TokSystemCall;}


{B}             {TRACE;}
{N}             {TRACE; return eol;}

\?              {TRACE; return '?';}

\(              {TRACE; return '(';}
\)              {TRACE; return ')';}
\,              {TRACE; return ',';}
\'              {TRACE; return TokQUOTE;}
\@              {TRACE; return TokAT;}
\;              {TRACE; return ';';}
\:              {TRACE; return ':';}
\[              {TRACE; return '[';}
\]              {TRACE; return ']';}
\{              {TRACE; return '{';}
\}              {TRACE; return '}';}
=               {TRACE; return '=';}
!=              {TRACE; return TokDIFF;}
\-              {TRACE; return TokMINUS;}
\+              {TRACE; return TokPLUS;}
\*              {TRACE; return TokTIMES;}
"/"             {TRACE; return TokSLASH;}
\^              {TRACE; return TokPOWER;}
\|              {TRACE; return TokUNION;}
\&              {TRACE; return TokINTER;}
\~              {TRACE; return TokSETMINUS;}


Mod             {TRACE; return TokMOD;}

While           {TRACE; return TokWHILE;}
Do              {TRACE; return TokDO;}
Switch          {TRACE; return TokSWITCH;}
Case            {TRACE; return TokCASE;}
Default         {TRACE; return TokDEFAULT;}


If              {TRACE; return TokIF;}
Then            {TRACE; return TokTHEN;}
Else            {TRACE; return TokELSE;}

Foreach         {TRACE; return TokFOREACH;}

"=="            {TRACE; return TokEQ;}
"<"             {TRACE; return TokLT;}
"<="            {TRACE; return TokLTEQ;}
">"             {TRACE; return TokGT;}
">="            {TRACE; return TokGTEQ;}

And             {TRACE; return TokAND;}
Or              {TRACE; return TokOR;}
Not             {TRACE; return TokNOT;}
In              {TRACE; return TokIN;}

"->"            {TRACE; return TokRIGHTARROW;}
\'.\'           {TRACE; amllval.character = yytext[1]; return TokCharacter;}
_{S}            {TRACE;
                 amllval.String = new char[strlen(yytext)+1];
                 strcpy(amllval.String, yytext);
                 return TokFreeVar;}
{S}             {TRACE;
                 amllval.String = new char[strlen(yytext)+1];
                 strcpy(amllval.String, yytext);
                 return TokName;}
\"[^\"\n]*\"    {TRACE;
                 amllval.String = new char[strlen(yytext)-1];
                 strncpy(amllval.String, yytext+1,strlen(yytext)-2);
		 amllval.String[strlen(yytext)-2] = '\0';
		 return TokString;}
{D}		{TRACE; amllval.integer = atoi(yytext); return TokInt;}
{R}		{TRACE; amllval.real = atof(yytext); return TokReal;}

<<EOF>>     {TRACE;if(!popStream()) yyterminate();}
.		{TRACE; return TokError;}

%%
/*
const char* amlText() {

  return yytext;

}
*/
void Trace(char* s) {

  static char previous_token = '\n';

  if (s[0] == '\n') {
#ifdef LEXDEBUG
    if (previous_token != '\n') std::cerr << std::endl;
#endif
    previous_token = '\n';
  }
  else {
    previous_token = yytext[0];
#ifdef LEXDEBUG
    std::cerr << "[" << s << "]" << std::flush;
#endif
  }
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

// redefined since lex uses the option -P and the default
// yywrap is nolonger provided by the lex library -lfl
int yywrap() {

  return 1;

}

const char* amlCurrentLine() {

  return curr_line_buf;

}

void amlPointOnInputBuffer(const char* buff) {

  assert(buff);

  reset_curr_line_buf();
  string_buff = buff;

}

