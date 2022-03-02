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
 *       $Id: erroraml.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef ERRORAML_HEADER
#define ERRORAML_HEADER

#include <iostream>
#include "tool/config.h"
#ifdef STL_EXTENSION
        #include <sstream>
#else
        #include <strstream>
#endif

#include "tool/rw_cstring.h"
#include "tool/rw_list.h"
//#include <rw/tvslist.h>
//#include <rw/cstring.h>

#include "defs.h"
#include "kernel_err.h"

#define AMLCOMPLETEERRORITEM(x)  {\
                               assert(getAMLErrorList()); \
                               assert(getAMLErrorList()->getLastAMLErrorItem()); \
                               getAMLErrorList()->getLastAMLErrorItem()->complete(ERRORMSG(x)); \
                             }


class AMLErrorItem {

  friend class AMLErrorList;
  friend std::ostream& operator<<(std::ostream&, const AMLErrorItem&);

  RWCString _module;

  int _line_nb;
  int _column_nb;

  RWCString _input_line;
  RWCString _complete_input_line;

  RWCString _message;
  int _err_pos;

  RWCString _File;
  int _Line;
  int _Token;

public:

  AMLErrorItem();
  AMLErrorItem(
               const char* module,
               int token,
               const char* input_line,
               const char* complete_line,

               const char* srcfile = NULL, // optional arguments ...
               int srcline = UNDEF,
               const char* message = "Error message not yet implemented",
               int line_nb = UNDEF,
               int column_nb = UNDEF,
               int err_pos = UNDEF
               );

  AMLErrorItem(const AMLErrorItem&);

  AMLErrorItem& operator=(const AMLErrorItem&);
  AmlBoolean operator==(const AMLErrorItem&);

  void complete(const char* file, int line, const char* module, const char* message);

  std::ostream& print(std::ostream&) const;

};

typedef RWTValDlist<AMLErrorItem> AMLErrorItemList;
typedef RWTValDlistIterator<AMLErrorItem> AMLErrorItemListIter;

static const unsigned int MAXERROR = 3;

class AMLErrorList : public AMLErrorItemList {

  friend std::ostream& operator<<(std::ostream&, const AMLErrorList&);

  unsigned int _MAXERRORS;

public:

  AMLErrorList(unsigned int maxerrors = MAXERROR);
  ~AMLErrorList() {}

  unsigned int& maxErrorNb() {return _MAXERRORS;}

  AMLErrorItem* getLastAMLErrorItem() {
    if (entries()) return &(AMLErrorItem&)at(entries()-1);
    else return 0;
  }

  void insert(const AMLErrorItem& item) {if (entries() < _MAXERRORS) AMLErrorItemList::insert(item);}

  std::ostream& print(std::ostream& o) const;
  void printLastAMLErrorItem(std::ostream& o) const;

};

std::ostream& operator<<(std::ostream& o, const AMLErrorItem& i);
std::ostream& operator<<(std::ostream& o, const AMLErrorList& l);

#endif
