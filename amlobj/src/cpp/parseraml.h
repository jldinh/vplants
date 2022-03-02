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
 *       $Id: parseraml.h 4122 2007-12-20 17:52:56Z dufourko $
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




#ifndef PARSERAML_HEADER
#define PARSERAML_HEADER

#include <stdio.h>
#include <string.h>
#include <sys/types.h>


#include "erroraml.h"

#include "defs.h"

#include "ammodel.h"
#include "amobjtable.h"
#include "global.h"
#include "gnuplot.h"

typedef int (*NextLineFunc)(char*);

extern void amlEchoOn();
extern void amlEchoOff();

extern void initGetNextLineFunc(NextLineFunc pf);
extern int readline_file(char* buff);
extern int readline_interactive(char* buff);
extern int file_init_read_line(const char* file);
extern AMLErrorList* getAMLErrorList();
extern void initParser(std::ostream* stream = 0);
extern void cleanParser();
extern const char* amlTokenName(int token);

extern std::ostream& getAMLOutputStream();

extern bool pushInclude(const AMObjVector& v);
extern bool pushFile(const char* file);
extern bool popStream();
extern "C" {

extern int amllex();
extern int amlparse();

extern int amlerror(char*);

//extern FILE* yyin;
//extern FILE* yyout;

}

#endif
