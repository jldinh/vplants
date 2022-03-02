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
 *       $Id: lsystemToMTG_scanner.l 5746 2008-11-26 08:55:28Z cokelaer $
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


/* 			
 * Template lexer in a multiple lexer/parser program. 
 *  The changes with respect to a normal lexer are indicated
 *  by brackets made of the following strings:
 *  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
 *       changes ...
 *  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
 */

%{ //-*-c++-*-


  // flags that control the debugging

  /* to create a lexer that will not collide with another lexer
     created on the same principle, the class created by flex++ must
     have a unique name.  this is why we must create a file template_scanner2.h
     containing :

// #define GENERIC_LEXER RecursiveLexer2 

     to define the new scanner class name (RecursiveLexer2 is the
     unique name identifying the current parser). This class
     encompasses the full state of the scanner and the scanner itself
     is implemented by its virtual method yylex(). This statement
     must be included before each :

// #include "tool/gscanner.h"	

     (see also call_parser2.C).

     Also, the function yywrap which is used in yylex() to detect 
     a new stream in case of EOF must be provided since the default
     version has name yywrap and is provided by the flex library
     (in C).

   */

#if 0
#define LEXDEBUG
#if 0
#define PRINT_LINE_AND_COLUMN
#endif
#endif
 
#include <fstream>
#include <list>

/*<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<*/
#include "lsystemToMTG_scanner.h"
/*>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>*/

#include "tool/gscanner_imp.h"		// to access to the generic scanner
#include "tool/gscanner.h"	

/*<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<*/
#ifdef BISON_HPP
#include "lsystemToMTG_parser.hpp"	// definition of the parser tokens
#else
#include "lsystemToMTG_parser.cpp.h"	// definition of the parser tokens
#endif
/*>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>*/

 using namespace std;

/*<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<*/
  // in a scanner with a prefix different from yy (here template2_yy), the
  // function yywrap must be redefined since we cannot use the default
  // definition yywrap defined by default in the flex lib (in C). This
  // function is used when EOF is encountered to check whether the
  // scanner should resume scanning on a new stream. If true the
  // scanner stops.

// remove the following block, which is not needed anymore (although we must add the code
// "%option noyywrap;" later on (see below).

//extern "C" {
//  int lsystemToMTG_yywrap() {return 1;} // if 0 then it is assumed that the scanning continues

// redefined since lex uses the option -P and the default
// yywrap is nolonger provided by the lex library -lfl
//int yywrap();
//}
/*>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>*/

%}

/* 
   %option c++ is equivalent to compiling with flex++.
   %option yyclass only applies when generating a C++ scanner (-+
   option).  It informs flex that you have derived foo as a subclass
   of yyFlexLexer, so flex will place your actions in the member func­
   tion foo::yylex() instead of yyFlexLexer::yylex().  It also
   generates a yyFlexLexer::yylex() member function that emits a
   run-time error (by invoking yyFlexLexer::LexerError()) if called.  

   %pointer yytext grows dynamically to accommodate large tokens.
    While this means your %pointer scanner can accommodate very
    large tokens (such as matching entire blocks of comments),
    bear in mind that each time the scanner must resize yytext it
    also must rescan the entire token from the beginning, so
    matching such tokens can prove slow.
   
*/

%option c++
%option yyclass="GENERIC_LEXER"
%option yylineno
/*<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<*/
%option prefix="lsystemToMTG_yy"
/*>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>*/
%pointer  
%option noyywrap
/* lex states */

%x include	 
%x comment

C   [a-zA-Z]
D	[0-9]+
R	[+-]?({D}"."{D}?)|({D}?"."{D})|({D}("."{D}?)?[Ee][+-]?{D})|("."{D}[Ee][+-]?{D})

%%

 /* yyterminate() could be used directly within the lexer if
    used in stand alone mode instead of return TokQUIT */

\[		{TRACE; return '[';}
\]		{TRACE; return ']';}
\(		{TRACE; return '(';}
\)		{TRACE; return ')';}
\,		{TRACE; return ',';}

\?P		{TRACE; VAL->character = YYText()[1]; return TokQuery;}
\?H		{TRACE; VAL->character = YYText()[1]; return TokQuery;}
\?L		{TRACE; VAL->character = YYText()[1]; return TokQuery;}
\?U		{TRACE; VAL->character = YYText()[1]; return TokQuery;}
\?E		{TRACE; VAL->character = YYText()[1]; return TokQuery;}

\;		{TRACE; VAL->character = YYText()[0]; return TokChar;}
\#		{TRACE; VAL->character = YYText()[0]; return TokChar;}
\-		{TRACE; VAL->character = YYText()[0]; return TokChar;}
\+		{TRACE; VAL->character = YYText()[0]; return TokChar;}

{C}		{TRACE; VAL->character = YYText()[0]; return TokChar;}

"\n"    {TRACE;}
{D}		{TRACE; VAL->integer = atoi(YYText()); return TokInt;}
{R}		{TRACE; VAL->real = atof(YYText()); return TokReal;}

<<EOF>>         {Trace("EOF");if (!popStream()) yyterminate();}
.		{Trace("unmatched");


#ifdef LEXDEBUG
         printChar(*YYText());
#endif
		 return TokError;}

%%

