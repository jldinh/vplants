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
 *       $Id: error.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef ERROR_HEADER
#define ERROR_HEADER

#include <iostream>

#include "tool/config.h"
#ifdef STL_EXTENSION
	#include <sstream>
#else
	#include <strstream>
#endif

#include "tool/rw_list.h"
#include "tool/rw_cstring.h"
//#include <rw/tvslist.h>
//#include <rw/cstring.h>

#include "aml/defs.h"


extern char* LOGICALERR;

#define ISFALSE(x) (!(x))
#define VALID(x)   (x>=0)

#ifdef DEBUGCHECKERROR
#define COMPLETEERRORITEM(x) getErrorList()->completeLastErrorItem(__FILE__,__LINE__,x)
#define COMPLETEERRORITEM1(x,y) getErrorList()->completeLastErrorItem(__FILE__,__LINE__,x,y)
#define COMPLETEERRORITEM2(x,y,z) getErrorList()->completeLastErrorItem(__FILE__,__LINE__,x,y,z)
#else
#define COMPLETEERRORITEM(x) getErrorList()->completeLastErrorItem(x)
#define COMPLETEERRORITEM1(x,y) getErrorList()->completeLastErrorItem(x,y)
#define COMPLETEERRORITEM2(x,y,z) getErrorList()->completeLastErrorItem(x,y,z)
#endif

class ErrorItem {

  friend class ErrorList;
  friend std::ostream& operator<<(std::ostream&, const ErrorItem&);

  int _type;
  int _code;
  int _line_nb;
  int _column_nb;
  RWCString _input_line;
  RWCString _complete_input_line;
  RWCString _message;
  int _err_pos;
  int _cf_ligne;

#ifdef DEBUGCHECKERROR
  RWCString _File;
  int _Line;
  int _Token;
#endif

public:

  ErrorItem();
  ErrorItem(
#ifdef DEBUGCHECKERROR
            const char* srcfile,
            int srcline,
            int token,
#endif
            const char* message,
            int type,
            int code,
            int line_nb,
            int column_nb,
            const char* input_line,
            const char* complete_line,
            int err_pos,
            int cf_ligne);
  ErrorItem(const ErrorItem&);

  ErrorItem& operator=(const ErrorItem&);
  AmlBoolean operator==(const ErrorItem&);

  int& type() {return _type;}
  int& code() {return _code;}
  int& lineNb() {return _line_nb;}
  int& columnNb() {return _column_nb;}
  RWCString& message() {return _message;}
  int& errPos() {return _err_pos;}
  int& cfLigne() {return _cf_ligne;}

  std::ostream& print(std::ostream&) const;

};

std::ostream& operator<<(std::ostream& o, const ErrorItem& i);


typedef RWTValDlist<ErrorItem> ErrorItemList;
typedef RWTValDlistIterator<ErrorItem> ErrorItemListIter;

class ErrorList : public ErrorItemList {

  friend std::ostream& operator<<(std::ostream&, const ErrorList&);

  const char** _errmsg;
  const char** _errtypes;

  std::ostream& _err_output;

  int _MAXERRORS;

public:

  ErrorList(const char** errmsg, const char** errtypes, std::ostream& errfile = std::cerr, int maxerrors = FILEMAXERROR);
  ~ErrorList() {}

  int& maxErrorNb() {return _MAXERRORS;}

  ErrorItem* getLastErrorItem();

  int completeLastErrorItem(
#ifdef DEBUGCHECKERROR
                      const char* srcfile,
                      int srcline,
#endif
                      int errmess,
                      const char* s1 = NULL, const char* s2 = NULL);


  std::ostream& print(std::ostream& o) const;
  void printLastErrorItem(std::ostream& o) const;
};

std::ostream& operator<<(std::ostream& o, const ErrorList& l);

#endif
