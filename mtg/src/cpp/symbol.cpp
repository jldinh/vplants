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
 *       $Id: symbol.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "symbol.h"

using namespace std;

MySymbol::MySymbol(const  char* file_name,
                   const  char* symbol_name,
                   char a_symb)
{
  _fileName=new RWCString (file_name);
  _symbolName=new RWCString (symbol_name);
  _symbol=a_symb;
}

MySymbol::MySymbol(const MySymbol& symbol)
{
  symbolCopy(symbol);
}

MySymbol::MySymbol(const char a_symb)
{
  _symbol=a_symb;
  _fileName=new RWCString;
  _symbolName=new RWCString;
}

MySymbol::MySymbol()
{
  _fileName=new RWCString;
  _symbolName=new RWCString;
  _symbol=UNDEF;
}

MySymbol::~MySymbol()
{
  clearAndDestroy();
}

const RWCString& MySymbol::getSymbolFileName() const
{
  return *_fileName;
}

const RWCString& MySymbol::getSymbolName() const
{
  return *_symbolName;
}

AmlBoolean MySymbol::operator==(const MySymbol& sym ) const
{
  AmlBoolean result=FALSE;

  if (_symbol==sym._symbol)
  {
    result=TRUE;
  }

  return result;
}

const MySymbol& MySymbol::operator=(const MySymbol& symbol)
{
  if (this!=&symbol)
  {
    clearAndDestroy();
    symbolCopy(symbol);
  }

  return *this;
}

void MySymbol::clearAndDestroy()
{
  delete _fileName;
  delete _symbolName;
}

void MySymbol::symbolCopy(const MySymbol& symbol)
{
  _fileName=new RWCString (symbol._fileName->data());
  _symbolName=new RWCString (symbol._symbolName->data());
  _symbol=symbol._symbol;
}

AmlBoolean MySymbol::isValid()
{
  AmlBoolean result=TRUE;


  return result;
}


SymbLib::SymbLib()
{
  _symbList=new SymbolsTable;
}

SymbLib::~SymbLib()
{
  delete _symbList;
}

AmlBoolean SymbLib::addSymbol(const MySymbol symbol)
{
  if (!_symbList->contains(symbol))
  {
    _symbList->insert(symbol);

    return TRUE;
  }
  else
  {
    return FALSE;
  }
}

const MySymbol SymbLib::lookForASymbol(const char a_symb) const
{
  MySymbol test_s(a_symb);

  size_t index=_symbList->index(test_s);

  if (index!=RW_NPOS)
  {
    return _symbList->at(index);
  }
  else
  {
//    return /* *new */ MySymbol ("nentn105","entrenoeud",a_symb);
    return /* *new */ MySymbol ("","",a_symb);
  }
}

void SymbLib::clear()
{
  _symbList->clear();
}

void SymbLib::report() const
{
  cout << "----------------------------------------------" << endl;
  cout << "#          Symbol's library report           #" << endl;
  cout << "----------------------------------------------" << endl;
  cout << endl << endl;

  IntType nb=_symbList->entries();

  cout << "Number of symbols : " << nb << endl;

  for(IntType i=0;i<nb;i++)
  {
    MySymbol symbol=_symbList->at(i);

    cout << "Pattern's file name : " << symbol.getSymbolFileName() << endl;
    cout << "Pattern name        : " << symbol.getSymbolName() << endl;
    cout << "Symbol              : " << symbol.getSymbol() << endl;
  }
}


const SymbolsTable& SymbLib::getSymbolsTable() const
{
  return *_symbList;
}







