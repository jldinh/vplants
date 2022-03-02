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
 *       $Id: forms.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "forms.h"

using namespace std;

Forms::Forms()
{
  _category=UNDEF;
}

Forms::Forms(const Forms& form)
{
  _category=form._category;
}

Forms::Forms(IntType category)
{
  _category=category;
}

AmlBoolean Forms::operator==(const Forms& form) const
{
  AmlBoolean result=FALSE;

  if (_category==form._category)
  {
    result=TRUE;
  }

  return result;
}

AmlBoolean Forms::operator<(const Forms& form) const
{
  AmlBoolean result=FALSE;

  if (_category<form._category)
  {
    result=TRUE;
  }

  return result;
}

const Forms& Forms::operator=(const Forms& form)
{
  if (this!=&form)
  {
    _category=form._category;
  }

  return *this;
}


BezierForm::BezierForm(ListOfMyVectors& vec_list,
                       IntType category) : Forms(category)
{
  _controlPoints=new ListOfMyVectors (vec_list);
  _saveControlPoints=new ListOfMyVectors (vec_list);
  _details=300;
  _curveLength=curveLength();
  _details=-1;
}

BezierForm::~BezierForm()
{
  delete _controlPoints;
  delete _saveControlPoints;
}

void BezierForm::modifBranchForm(BranchCompoList& branch_compo)
{

  _details=branch_compo.entries();

  ValType branch_length=0;

  for (IntType i=0;i<_details;i++)
  {
    branch_length+=branch_compo.at(i).getLength();
  }

  ValType factor=branch_length/_curveLength;

  changeScale(factor);

  IntType nb=_controlPoints->entries();

  ValType step=branch_compo.at(0).getLength()/branch_length;

  ValType u=0;

  ValType beta=branch_compo.at(0).getBeta();

  for (IntType indice=0;indice<_details;indice++)
  {
    MyVector v1 (Bezier(u));
    MyVector v2 (Bezier(u+step));
    MyVector direction=v2-v1;

    ValType alpha=direction.computeAlpha();
    ValType bet=direction.computeBeta();

    step=branch_compo.at(indice).getLength()/branch_length;

    branch_compo.at(indice).putAlpha(alpha);
    branch_compo.at(indice).putBeta(beta);

    u+=step;
  }
}


ValType BezierForm::Berstein(IntType i,
                             IntType n,
                             ValType u)
{
  ValType result;

  result=(fact(n)/(fact(i)*fact(n-i))*power(u,i)*power((1-u),n-i));

  return result;
}


MyVector BezierForm::Bezier(ValType u)
{
  IntType nb=_controlPoints->entries();
  ValType x,y,z;

  x=y=z=0;

  for(IntType i=0;i<nb;i++)
  {
    x+=Berstein(i,nb-1,u)*_controlPoints->at(i)[0];
    y+=Berstein(i,nb-1,u)*_controlPoints->at(i)[1];
    z+=Berstein(i,nb-1,u)*_controlPoints->at(i)[2];
  }

  MyVector result(x,y,z);

  return result;
}


ValType BezierForm::curveLength()
{
  ValType result=0;
  IntType i=0;
  ValType step=1/(ValType)_details;

  for(ValType u=0;u<1;u+=step)
  {
    MyVector coord=Bezier(u+step)-Bezier(u);
    result+=coord.computeLength();
    i++;
  }

  return result;
}


void BezierForm::changeScale(ValType factor )
{
  IntType nb=_controlPoints->entries();

  for (IntType i=0;i<nb;i++)
  {
    ValType x=_saveControlPoints->at(i)[0]*factor;
    ValType y=_saveControlPoints->at(i)[1]*factor;
    ValType z=_saveControlPoints->at(i)[2]*factor;
    MyVector v(x,y,z);
    _controlPoints->at(i)=v;
  }
}

ValType BezierForm::fact(IntType n)
{
  if (n==0)
  {
    return 1;
  }
  else
  {
    return n*fact(n-1);
  }
}

ValType BezierForm::power(ValType x,
                          IntType n)
{
  return (ValType)pow(x,(ValType)n);
}

void BezierForm::report()
{
  Forms::report();
  cout << "Control points : " << endl;

  for(IntType j=0;j<_saveControlPoints->entries();j++)
  {
    _saveControlPoints->at(j).report();
  }
}



FormsLib::FormsLib()
{
  _formsList=new ListOfForms;

  /*
  ListOfMyVectors* list=new ListOfMyVectors;

  MyVector v1(0,0,0);
  MyVector v2(0,4,6);
  MyVector v3(0,14,6);

  list->insert(v1);
  list->insert(v2);
  list->insert(v3);

  Forms* form=new BezierForm (*list,UNDEF);

  _formsList->insert(form);

  delete list;
  */
}

FormsLib::~FormsLib()
{
  _formsList->clearAndDestroy();
  delete _formsList;
}

void FormsLib::addForm(Forms& form)
{
  if (!_formsList->contains(&form))
  {
    _formsList->insert(&form);
  }
}

Forms* FormsLib::lookForAForm(IntType category)
{
  Forms* form=new Forms (category);
  size_t index=_formsList->index(form);

  delete form;

  if (index!=RW_NPOS)
  {
    return _formsList->at(index);
  }
  else
  {
    // cerr << "category not found " << endl;
    return NULL;
  }

}

void FormsLib::clear()
{
  _formsList->clearAndDestroy();
}

void FormsLib::report()
{
  // For debbugging.

  cout << "There's " << _formsList->entries() << " curves." << endl;

  for(IntType i=0;i<_formsList->entries();i++)
  {
    _formsList->at(i)->report();
  }

}



