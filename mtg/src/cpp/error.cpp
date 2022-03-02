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
 *       $Id: error.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include <iomanip> // AML2: For setw()
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "tool/rw_tokenizer.h"
//#include <rw/ctoken.h>

#ifndef STL_EXTENSION
  #ifndef _WIN32
    #define FORM
  #endif
#endif

#ifdef FORM
#include <features.h>
#include <stream.h>   //for the use of function extern char* form(const char* ...); (printf format)
#endif



#include <assert.h>
#include <strstream>

#include "error.h"


#if 1
#define DEBUGATRUNTIME
#endif

using namespace std;

static const int MAXERRMESSAGELENGTH = 500;

// --------     Class ErrorItem

ErrorItem::ErrorItem() {

#ifdef DEBUGCHECKERROR
  _File = "";
  _Line = -1;
  _Token = -1;
#endif

  _message = ""; // RWCString& operator=(const char*)
  _type = 0;
  _code = 0;
  _line_nb = 0;
  _column_nb = 0;
  _input_line = "";
  _complete_input_line = "";
  _err_pos = 0;
  _cf_ligne = 0;


}

ErrorItem::ErrorItem(
#ifdef DEBUGCHECKERROR
                     const char* srcfile,
                     int srcline,
                     int token,
#endif
                     const char* message,
                     int type = 0,
                     int code = UNDEF,
                     int line_nb = UNDEF,
                     int column_nb = UNDEF,
                     const char* input_line = NULL,
                     const char* complete_input_line = NULL,
                     int err_pos = UNDEF,
                     int cf_ligne = UNDEF)
{

#ifdef DEBUGCHECKERROR
  if (srcfile) _File = srcfile;
  _Line = srcline;
  _Token = token;
#endif

  _message = message; // RWCString& operator=(const char*)
  _type = type;
  _code = code;
  _line_nb = line_nb;
  _column_nb = column_nb;
  _input_line = input_line;
  _complete_input_line = complete_input_line;
  _err_pos = err_pos;
  _cf_ligne = cf_ligne;

}

ErrorItem::ErrorItem(const ErrorItem& err) {

#ifdef DEBUGCHECKERROR
  _File = err._File;
  _Line = err._Line;
  _Token = err._Token;
#endif

  _message = err._message; // RWCString& operator=(const char*)
  _type = err._type;
  _code = err._code;
  _line_nb = err._line_nb;
  _column_nb = err._column_nb;
  _input_line = err._input_line;
  _complete_input_line = err._complete_input_line;
  _err_pos = err._err_pos;
  _cf_ligne = err._cf_ligne;

}

ErrorItem& ErrorItem::operator=(const ErrorItem& err) {

  if (this == &err) return *this;
  else {

#ifdef DEBUGCHECKERROR
    _File = err._File;
    _Line = err._Line;
    _Token = err._Token;
#endif

    _message = err._message; // RWCString& operator=(const char*)
    _type = err._type;
    _code = err._code;
    _line_nb = err._line_nb;
    _column_nb = err._column_nb;
    _input_line = err._input_line;
    _complete_input_line = err._complete_input_line;
    _err_pos = err._err_pos;
    _cf_ligne = err._cf_ligne;

  }
  return *this;

}

AmlBoolean ErrorItem::operator==(const ErrorItem& err) {

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

ostream& ErrorItem::print(ostream& o) const {

  char partial_line[MAXLINELENGTH];

  RWCString locs;
  RWCString token;

  strcpy(partial_line, _input_line.data());

  istrstream istr(partial_line);

  int state = FALSE;
  int i;

  while (state == FALSE) {

    if (token.readToDelim(istr, '\t').eof()) state = TRUE;

    if (state == FALSE) {

      for(i=0; i<token.length(); i++) locs += " ";

      locs += "\t";

    }
    else
    if (token.length() == 0) for(i=0; i<6; i++) locs += "^"; // case of a token \t
    else for(i=0; i<token.length(); i++) locs += "^";

  }

  o << endl;
  o << "*** ERROR : " << _type;
#ifdef DEBUGCHECKERROR
  o << " ... detected in source FILE: " << _File.data() <<
  ", LINE:  " << _Line;
  // ", on : " << tokenName(_Token) << " = '" << _Token << "'";
#endif
  o << endl;
  o << "*** line   " << setw(5) << _line_nb   << ": " << _complete_input_line;
  o << "*** column " << setw(5) << _column_nb << ": " << locs.data() << endl;
  o << "*** --> " <<  _message << endl;

return o;

}

ostream& operator<<(ostream& o, const ErrorItem& i) {return i.print(o);}


// --------     Class ErrorList

ErrorList::ErrorList(const char** errmsg, const char** errtypes, ostream& errfile, int max):
  _errmsg(errmsg),
  _errtypes(errtypes),
  _err_output(errfile)
{

  _MAXERRORS = max;

}


void ErrorList::printLastErrorItem(ostream& o) const {

  if (entries()) o << at(entries()-1);
  else o << "No item in the Error List" << endl;

}


int ErrorList::completeLastErrorItem(
#ifdef DEBUGCHECKERROR
                                     const char* srcfile,
                                     int srcline,
#endif
                                     int errmess,
                                     const char* s1, const char* s2) {

  static char curr_err_mess[MAXERRMESSAGELENGTH];

#ifdef FORM
  ostrstream ost(curr_err_mess, MAXERRMESSAGELENGTH);

  if (s1 == NULL && s2 == NULL) ost << _errmsg[errmess] << ends;
  else
    if (s1 != NULL && s2 == NULL) ost << form(_errmsg[errmess], s1) << ends;
  else
  if (s1 != NULL && s2 != NULL) ost << form(_errmsg[errmess], s1, s2) << ends;
  else
  assert(FALSE);
#else
  if (s1 == NULL && s2 == NULL) sprintf(curr_err_mess,_errmsg[errmess]);
  else
  if (s1 != NULL && s2 == NULL) sprintf(curr_err_mess,_errmsg[errmess],s1);
          // ost.form(_errmsg[errmess], s1) << ends;
  else
  if (s1 != NULL && s2 != NULL) sprintf(curr_err_mess,_errmsg[errmess],s1,s2);
          // ost.form(_errmsg[errmess], s1, s2) << ends;
  else
  assert(FALSE);
#endif

  assert(entries());

  at(entries()-1)._message = curr_err_mess; // RWCString& operator=(const char*)
#ifdef DEBUGCHECKERROR
  if (srcfile) at(entries()-1)._File = srcfile;
  at(entries()-1)._Line = srcline;
#endif

#ifdef DEBUGATRUNTIME
  printLastErrorItem(_err_output);
#endif

  return 1;

}


ostream& ErrorList::print(ostream& o) const {

  ErrorItemListIter next( *(ErrorList*) this);

  o << endl << endl;

  while (next()) {

    o << next.key() << endl;

  }

  return o;

}

ostream& operator<<(ostream& o, const ErrorList& l) {return l.print(o);}

