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
 *       $Id: mynode.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "mynode.h"

MyNode::MyNode(VId vertex)
{
  _lessSons=new VIdList;
  _plusSons=new VIdList;   
  _vertex=vertex;
  _father=UNDEF;
}

MyNode::MyNode(VId vertex,
	       VId father,
	       const VIdList* plus_list,
	       const VIdList* less_list)
{
  _lessSons=new VIdList (*less_list);
  _plusSons=new VIdList (*plus_list);
  
  _vertex=vertex;
  _father=father;
}

MyNode::MyNode(VId vertex, VId father)
{ 
  _lessSons=new VIdList;
  _plusSons=new VIdList;
  
  _vertex=vertex;
  _father=father;
}

MyNode::MyNode(const MyNode& a_node)
{ 
  construct(a_node);
}

MyNode::MyNode()
{ 
  _lessSons=new VIdList;
  _plusSons=new VIdList;
  
  _vertex=UNDEF;
  _father=UNDEF;
}

MyNode::~MyNode()
{
  clearAndDestroy();
}

AmlBoolean MyNode::operator<(const MyNode& a_node) const
{
  AmlBoolean result=FALSE;

  if (_vertex<a_node._vertex)
  {
    result=TRUE;
  }

  return result;
}

AmlBoolean MyNode::operator==(const MyNode& a_node) const
{
  AmlBoolean result=FALSE;

  if (_vertex==a_node._vertex)
  {
    result=TRUE;
  }

  return result;
}

const MyNode& MyNode::operator=(const MyNode& a_node)
{
  if (this!=&a_node)
  {
    clearAndDestroy();
    construct(a_node);
  }

  return *this;
}

void MyNode::addLessSons(VId vertex)
{
  _lessSons->insert(vertex);
}

void MyNode::addLessSons(const VIdList* list)
{
  IntType nb=list->entries();
  
  for(IntType i=0;i<nb;i++)
  {
    addLessSons(list->at(i));
  }

}

void MyNode::addPlusSons(VId vertex)
{
  _plusSons->insert(vertex);
}

  
void MyNode::addPlusSons(const VIdList* list)
{
  IntType nb=list->entries();
  
  for(IntType i=0;i<nb;i++)
  {
    addPlusSons(list->at(i));
  }
}

void MyNode::clearAndDestroy()
{
  delete _plusSons;
  delete _lessSons;
}

void MyNode::construct(const MyNode& a_node)
{
  _vertex=a_node._vertex;
  _father=a_node._father;
  _plusSons=new VIdList (*a_node._plusSons);
  _lessSons=new VIdList (*a_node._lessSons);
  
}

void MyNode::putFather(VId father)
{
  _father=father;
}

void MyNode::putRelation(EType edge)
{
  _relation=edge;
}
