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
 *       $Id: branch.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "branch.h"

using namespace std;

BranchElement::BranchElement(const BranchElement& b)
{
  _length=b._length;
  _topdia=b._topdia;
  _botdia=b._botdia;
  _alpha=b._alpha;
  _beta=b._beta;
  _vertex=b._vertex;
  _dirp=b._dirp;
  _dirs=b._dirs;
  _origin=b._origin;

}

BranchElement::BranchElement(const ValType length,
                             const ValType alpha,
                             const ValType beta,
                             const ValType botdia,
                             const ValType topdia,
                             const VId vertex)

{
  _length=length;
  _alpha=alpha;
  _beta=beta;
  _botdia=botdia;
  _topdia=topdia;
  _vertex=vertex;
}



BranchElement::BranchElement( const VId vertex)
{
  _vertex=vertex;
  _length=VAL_ERROR;
  _alpha=VAL_ERROR;
  _botdia=VAL_ERROR;
  _topdia=VAL_ERROR;
  _beta=0;
}

BranchElement::BranchElement()
{
  _vertex=UNDEF;
  _length=VAL_ERROR;
  _alpha=VAL_ERROR;
  _beta=VAL_ERROR;
  _botdia=VAL_ERROR;
  _topdia=VAL_ERROR;
  _beta=0;
}

BranchElement::~BranchElement()
{
}

AmlBoolean BranchElement::operator==(const BranchElement& b ) const
{
  if (_vertex==b._vertex)
  {
    return TRUE;
  }
  else
  {
    return FALSE;
  }
}

const BranchElement& BranchElement::operator=(const BranchElement& b )
{

  if (this!=&b)
  {
    _length=b._length;
    _topdia=b._topdia;
    _botdia=b._botdia;
    _alpha=b._alpha;
    _beta=b._beta;
    _vertex=b._vertex;
    _dirp=b._dirp;
    _dirs=b._dirs;
    _origin=b._origin;

  }

  return *this;
}

AmlBoolean BranchElement::isValid() const
{

  AmlBoolean result=FALSE;

  if ((_length!=VAL_ERROR) &&
      (_topdia!=VAL_ERROR) &&
      (_botdia!=VAL_ERROR) &&
      (_alpha!=VAL_ERROR) &&
      (_beta!=VAL_ERROR) &&
      (_vertex!=VAL_ERROR))
  {
    result=TRUE;
  }

  return result;
}


void BranchElement::putLength(const ValType l)
{
  _length=l;
}

void BranchElement::putTopDia(const ValType t)
{
  _topdia=t;
}

void BranchElement::putBotDia(const ValType b)
{
  _botdia=b;
}

void BranchElement::putVertex(const VId v)
{
  _vertex=v;
}

void BranchElement::putDirp(const MyVector v)
{
  _dirp=v;
}

void BranchElement::putDirs(const MyVector v)
{
 _dirs=v;
}

void BranchElement::putOrigin(const MyVector v )
{
 _origin=v;
}

void BranchElement::putAlpha(const ValType a)
{
  _alpha=a;
}

void BranchElement::putBeta(const ValType b)
{
  _beta=b;
}

void BranchElement::report() const
{
  cout << "BRANCH-ELEMENT REPORT" << endl;
  cout << "---------------------" << endl << endl;

  cout << "Vertex : " << _vertex ;
  cout << "  Length : " << _length << endl;
  cout << "MyVectors : " << endl;
  cout << "Origin : ( " << _origin[0] << " , " << _origin[1] << " , " << _origin[2] << " )" << endl;
  cout << "Dirp   : ( " << _dirp[0] << " , " << _dirp[1] << " , " << _dirp[2] <<  " )" << endl;
  cout << "Dirs   : ( " << _dirs[0] <<  " , " <<_dirs[1] << " , " << _dirs[2] <<  " )" << endl;
  cout << "TopDia : " << _topdia << "  BotDia : " << _botdia << endl;
  cout << "Alpha  : " << _alpha  << "  Beta   : " << _beta << endl;
  cout << endl << endl;
  cout << "---------------------------------------------------------------------------------" << endl;
}

bool contains(const BranchCompoList& l, VId v){
  for(BranchCompoList::const_iterator _it = l.begin();
	  _it != l.end(); _it++)if(_it->getVertex() == v)return true;
  return false;
}

// Definition de la classe Branch.

Branch::Branch(const VId support, IntType pp)
{
  _support=support;
  _components=new BranchCompoList;
  _alpha=VAL_ERROR;
  _beta=VAL_ERROR;
  _category=UNDEF;
  _branchId=_branchCounter;
  _plantNumber=pp;
  _branchCounter++;
}

Branch::Branch(const Branch& b)
{
  _support=b._support;
  _components=new BranchCompoList (b.branchComponents());
  _alpha=b._alpha;
  _beta=b._beta;
  _category=b._category;
  _plantNumber=b._plantNumber;
  _branchId=b._branchId;
}

Branch::~Branch()
{
  delete _components;
}

const Branch& Branch::operator=(const Branch& b)
{
  if (this!=&b)
  {
    delete _components;
    _support=b._support;
    _components=new BranchCompoList (b.branchComponents());
    _alpha=b._alpha;
    _beta=b._beta;
    _category=b._category;
    _plantNumber=b._plantNumber;
  }

  return *this;
}

AmlBoolean Branch::operator==(const Branch& b) const
{

  AmlBoolean result=FALSE;

/*  if ((_support!=UNDEF) && (b._support!=UNDEF) && (_plantNumber==b._plantNumber))
  {
    if (_support==b._support)
    {
      result=TRUE;
    }
  }
  else
  {
    if (_branchId==b._branchId)
    {
      result=TRUE;
    }
  }*/

  if ((_plantNumber==b._plantNumber) && (_support==b._support))
  {
  //  if (_support==b._support)
  //  {
      result=TRUE;
  //   }
  }
  else
  {
    result=FALSE;
  }


  return result;

}

AmlBoolean Branch::operator<(const Branch& b) const
{
  AmlBoolean result=FALSE;

/*  if ((_support!=UNDEF) && (b._support!=UNDEF) && (_plantNumber==b._plantNumber))
  {
    if (_support<b._support)
    {
      result=TRUE;
    }
  }
  else
  {
    if (_branchId<b._branchId)
    {
      result=TRUE;
    }
  }*/



  if (_plantNumber==b._plantNumber)
  {
    if (_support<b._support)
    {
      result=TRUE;
    }
  }
  else
  {
    if (_plantNumber<b._plantNumber)
    {
      result=TRUE;
    }
  }

  return result;
}

VId Branch::baseOfBranch() const
{
  VId result=UNDEF;

  if (_components->entries()!=0)
  {
    result=_components->at(0).getVertex();
  }

  assert(result!=UNDEF);

  return result;

}

VId Branch::endOfBranch() const
{
  VId result=UNDEF;

  assert(_components->entries()!=0);

  IntType n=_components->entries();

  result=_components->at(n-1).getVertex();

  return result;
}

VId Branch::getSupport() const
{
  return _support;
}


void Branch::putCategory(IntType v)
{
  _category=v;
}

const BranchCompoList& 
Branch::branchComponents() const
{
  return *_components; 
}

void Branch::addElement(const BranchElement be)
{
  assert(!_components->contains(be));
  _components->insert(be);
//    _components->push_back(be);
}



