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
 *       $Id: erroraml.cpp 17611 2014-10-17 13:20:41Z pradal $
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
#include <stdio.h>
//#include <iostream.h>
#include <stdarg.h>
#include <string>

#include "tool/rw_tokenizer.h"
//#include <rw/ctoken.h>
//#include <rw/regexp.h>
#ifndef _WIN32
//#include <stream.h>   //for the use of function extern char* form(const char* ...); (printf format)
#endif
#include <assert.h>

#include "parseraml.h"
#include "erroraml.h"

#if 1
#define DEBUGERRORLINE
#endif

using namespace std;
/* Cette procedure serait mieux si on pouvait etre sur qu'elle est portable !!!!!! */
/* Si elle n'etait pas portable, utiliser la suivante qui fait le travail
   a la main */

void genAMLError(const char* file, int line, const char* module_name, const char* msg ...) {

  va_list args;                 // man vprintf
  va_start(args, msg);

  // Expand the error message

  char fullmsg[1000];

  vsprintf(fullmsg,msg,args);

  // Only the module name is set in the created AMLErrorItem
  amlerror((char*)module_name);

  assert(getAMLErrorList());
  assert(getAMLErrorList()->getLastAMLErrorItem());

  AMLErrorItem* erritem = getAMLErrorList()->getLastAMLErrorItem(); // get the created erroritem
  assert(erritem);

  erritem->complete(file, line, module_name, fullmsg); // module name is reset

  va_end(args);

}

// ------------------
// Class AMLErrorItem
// ------------------

AMLErrorItem::AMLErrorItem() {

  _File = "";
  _Line = -1;
  _Token = -1;

  _message = ""; // RWCString& operator=(const char*)
  _module = "";

  _line_nb = 0;
  _column_nb = 0;
  _input_line = "";
  _complete_input_line = "";
  _err_pos = 0;

}

AMLErrorItem::AMLErrorItem(
                           const char* module,
                           int token,
                           const char* input_line,
                           const char* complete_line,

                           const char* srcfile,
                           int srcline,

                           const char* message,

                           int line_nb,
                           int column_nb,

                           int err_pos
                           )
{


  if (srcfile) _File = srcfile;
  _Line = srcline;
  _Token = token;

  _message = message; // RWCString& operator=(const char*)
  _module = module;

  _line_nb = line_nb;
  _column_nb = column_nb;
  _input_line = input_line;
  _complete_input_line = complete_line;
  _err_pos = err_pos;

}

AMLErrorItem::AMLErrorItem(const AMLErrorItem& err) {

  _File = err._File;
  _Line = err._Line;
  _Token = err._Token;

  _message = err._message; // RWCString& operator=(const char*)
  _module = err._module;

  _line_nb = err._line_nb;
  _column_nb = err._column_nb;
  _input_line = err._input_line;
  _complete_input_line = err._complete_input_line;
  _err_pos = err._err_pos;

}

AMLErrorItem& AMLErrorItem::operator=(const AMLErrorItem& err) {

  if (this == &err) return *this;
  else {

    _File = err._File;
    _Line = err._Line;
    _Token = err._Token;

    _message = err._message; // RWCString& operator=(const char*)
    _module = err._module;

    _line_nb = err._line_nb;
    _column_nb = err._column_nb;
    _input_line = err._input_line;
    _complete_input_line = err._complete_input_line;
    _err_pos = err._err_pos;

  }
  return *this;
}

AmlBoolean AMLErrorItem::operator==(const AMLErrorItem& err) {

  if (this == &err) return TRUE;
  else {
    if (_message == err._message &&
        _line_nb == err._line_nb &&
        _column_nb == err._column_nb &&
        _input_line == err._input_line)

    return TRUE;
    else return FALSE;
  }

}

void AMLErrorItem::complete(const char* file, int line, const char* module, const char* message) {

  _File = file;
  _Line = line;

  _module = module;

  _message = message;

}

std::ostream& AMLErrorItem::print(std::ostream& o) const {

  char partial_line[MAXLINELENGTH];

  strcpy(partial_line, _input_line.data());

  RWCString locs;

  if (_input_line.length()) for(register size_t i=0; i<_input_line.length()-1; i++) locs += "-";

  locs += "^";

  o << endl;
  o << "*** ERROR : in " << _module << " module";
#ifdef DEBUGERRORLINE
  o << " ... detected in source FILE: " << _File.data() <<
  ", LINE:  " << _Line;
  o << ", on lookahead : " << amlTokenName(_Token) << " = '" << _Token << "'";
#endif
  o << endl;
  o << "*** line  : " << _complete_input_line;
  o << "*** at    : " << locs.data() << endl;
  o << "***  ---->  " <<  _message << endl;

return o;

}

ostream& operator<<(ostream& o, const AMLErrorItem& i) {return i.print(o);}


// ------------------
// Class AMLErrorList
// ------------------

AMLErrorList::AMLErrorList(unsigned int max) {

  _MAXERRORS = max;

}


void AMLErrorList::printLastAMLErrorItem(ostream& o) const {

  if (entries()) o << at(entries()-1);
  else o << "No item in the Error List" << endl;

}

ostream& AMLErrorList::print(ostream& o) const {

  AMLErrorItemListIter next( *(AMLErrorList*) this);

  o << endl << endl;

  while (next()) {

    o << next.key() << endl;

  }

  return o;

}

ostream& operator<<(ostream& o, const AMLErrorList& l) {return l.print(o);}

