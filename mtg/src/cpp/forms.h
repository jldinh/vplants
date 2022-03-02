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
 *       $Id: forms.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _FORMS_SAMIR_DEF_
#define _FORMS_SAMIR_DEF_

#include "tool/rw_vector.h"
//#include <rw/tpsrtvec.h>
#include "definitions.h"
#include "branch.h"
#include "vector.h"

class Forms
{

 public:

  Forms();
  Forms(IntType category);
  Forms(const Forms&);

  AmlBoolean operator==(const Forms&) const;
  AmlBoolean operator<(const Forms&) const;
  const Forms& operator=(const Forms&);


  virtual void modifBranchForm(BranchCompoList&) {assert(1==0);};
  virtual void report() {std::cout << "Category : " << _category << std::endl;};

 private:

  IntType _category;

};

typedef RWTPtrSortedVector<Forms> ListOfForms;

class BezierForm : public Forms
{

 public:

  BezierForm(ListOfMyVectors&,
             IntType);
  ~BezierForm();

  virtual void modifBranchForm(BranchCompoList& );
  virtual void report();

 private:

  ListOfMyVectors* _controlPoints;
  ListOfMyVectors* _saveControlPoints;
  IntType _details;
  ValType _curveLength;

  ValType Berstein(IntType, IntType, ValType );
  MyVector Bezier(ValType);
  ValType curveLength();
  ValType fact(IntType);
  ValType power(ValType,IntType);
  void changeScale(ValType );

};




class FormsLib
{
 public:

  FormsLib();

   // FormsLib(const char* file_name)
   // not yet implemented

  ~FormsLib();

  Forms* lookForAForm(IntType category);
  void addForm(Forms&);
  void clear();
  void report();

 private:

  ListOfForms* _formsList;
};


#endif
