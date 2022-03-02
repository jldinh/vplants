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
 *       $Id: diameters.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "aml/ammodel.h"

#include "definitions.h"
#include "attributes.h"
#include "plant.h"
#include "diameters.h"

#include "dressingfile.h"

using namespace std;

TopDia::TopDia(Plant* plant,
               const FNode* funct,
               const ValType scale):Measures(plant,funct,scale)
{
  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_TOPDIA)
    {
      _index=i;
    }
  }

  VId root=_plant->mtgRoot();

  if (_index!=UNDEF)
  {
    _level=lookForLevel(root);
  }

}

ValType TopDia::lookUpTopDia(const VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VId father=_plant->compoFather(vertex);

    if (father!=UNDEF)
    {
      VIdList* list=_plant->compoSons(father);

      if ((!list->isEmpty()) && (list->at(list->entries()-1)==vertex))
      {
        result=lookUpTopDia(father);
      }

      delete list;
    }
  }

  return result;
}


ValType TopDia::lookDownTopDia(const VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VIdList* list=_plant->compoSons(vertex);

    if (!list->isEmpty())
    {
      VId last_son=list->at(list->entries()-1);

      result=lookDownTopDia(last_son);
    }

    delete list;
  }

  return result;
}


ValType TopDia::lookForTopDia(const VId vertex) const
{

  ValType result=LUNDEF;

  if (_plant->vscale(vertex)>=_level)
  {
    result=lookUpTopDia(vertex);
  }
  else
  {
    result=lookDownTopDia(vertex);
  }

  return result;
}


// bottom dia definitions


BottomDia::BottomDia(Plant* plant,
                     const FNode* funct,
                     const ValType scale):Measures(plant,funct,scale)
{

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_BOTTOMDIA)
    {
      _index=i;
    }
  }

  VId root=_plant->mtgRoot();

  if (_index!=UNDEF)
  {
    _level=lookForLevel(root);
  }

}

ValType BottomDia::lookUpBottomDia(const VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VId father=_plant->compoFather(vertex);

    if (father!=UNDEF)
    {
      VIdList* list=_plant->compoSons(father);

      if ((!list->isEmpty()) && (list->at(0)==vertex))
      {
        result=lookUpBottomDia(father);
      }

      delete list;
    }
  }

  return result;
}


ValType BottomDia::lookDownBottomDia(const VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VIdList* list=_plant->compoSons(vertex);

    if (!list->isEmpty())
    {
      VId first_son=list->at(0);

      result=lookDownBottomDia(first_son);
    }

    delete list;
  }

  return result;
}


ValType  BottomDia::lookForBottomDia(const VId vertex) const
{

  ValType result=LUNDEF;

  if (_plant->vscale(vertex)>=_level)
  {
    result=lookUpBottomDia(vertex);
  }
  else
  {
    result=lookDownBottomDia(vertex);
  }

  return result;
}


// Classe Diameters.


Diameters::Diameters(Plant* plant,
                     const FNode* topf,
                     const FNode* botf,
                     const DressingFile* dressing_file,
                     const ValType scale=1):TopDia(plant,topf,scale),BottomDia(plant,botf,scale)
{
  _dressingFile=dressing_file;
  _areValidDiameters=TRUE;
}


void Diameters::passOne(Branch& branch)
{
  BranchCompoList* compo_list=branch._components;

  for(size_t i=0;i<compo_list->entries();i++)
  {
    ValType top_dia=lookForTopDia(compo_list->at(i).getVertex());
    ValType bot_dia=lookForBottomDia(compo_list->at(i).getVertex());

    compo_list->at(i).putTopDia(top_dia);
    compo_list->at(i).putBotDia(bot_dia);
  }
}

void Diameters::computeDiameters(Branch& branch)
{

  passOne(branch);

  BranchCompoList* compo_list=branch._components;
  IntType next_index=-1;
  AmlBoolean interpol_dia=TRUE;

  for(size_t i=0;i<compo_list->entries();i++)
  {
    BranchElement br_element=compo_list->at(i);

    ValType top_dia=UNDEF;
    ValType bot_dia=UNDEF;

    ValType father_top=0;
    ValType father_bot=0;

    if (i==0)
    {

      VId vertex=br_element.getVertex();
      VId father=TopDia::_plant->topoFather(vertex,ANY);

      if (father!=UNDEF)
      {
        BranchElement father_element=TopDia::_plant->searchForElement(father);
        father_top=father_element.getTopDia();
        father_bot=father_element.getBotDia();
        // cout << "diameters.C on recupere les diametres du support. Vertex ";
        // cout << vertex << endl;
      }
      else
      {

        // First look in the complexes to check whether there exists diameter info


        BranchElement start_br=compo_list->at(i);

        BranchElement next_bottom=nextDefinedBottomDia(branch,start_br);
        BranchElement next_sommit=nextDefinedTopDia(branch,start_br);

        size_t next_index1=compo_list->index(next_bottom);
        size_t next_index2=compo_list->index(next_sommit);

        if (next_index1==RW_NPOS)
        {
          next_index1=compo_list->entries()+1;
        }

        if (next_index2==RW_NPOS)
        {
          next_index2=compo_list->entries()+1;
        }

        if ((next_bottom.getVertex()!=UNDEF) && (next_index1<=next_index2))
        {
          father_top=next_bottom.getBotDia();
          father_bot=next_bottom.getBotDia();
        }
        else
        {
          if (next_sommit.getVertex()!=UNDEF)
          {
            father_top=next_sommit.getTopDia();
            father_bot=next_sommit.getTopDia();
          }
          else
          {
            father_top=_dressingFile->getMinTopDia(TopDia::_plant->symbol(vertex))/TopDia::_scale;
            father_bot=_dressingFile->getMinBotDia(BottomDia::_plant->symbol(vertex))/BottomDia::_scale;

           // cout << "Diameters: diametre par defaut. Vertex " << vertex << endl;
          }
        }
      }
    }
    else
    {
      father_top=compo_list->at(i-1).getTopDia();
      father_bot=compo_list->at(i-1).getBotDia();
    }

    if (br_element.getBotDia()==UNDEF)
    {
      bot_dia=father_top;
    }
    else
    {
      bot_dia=br_element.getBotDia();
    }

    if (br_element.getTopDia()==UNDEF)
    {
      if (interpol_dia)
      {
        BranchElement start_br;

        if (i<compo_list->entries()-1)
        {
          start_br=compo_list->at(i+1);
        }
        else
        {
          start_br=compo_list->at(i);
        }

       /* BranchElement next_bottom=nextDefinedBottomDia(branch,br_element);
        BranchElement next_sommit=nextDefinedTopDia(branch,br_element); */
        BranchElement next_bottom=nextDefinedBottomDia(branch,start_br);
        BranchElement next_sommit=nextDefinedTopDia(branch,start_br);

        size_t next_index1=compo_list->index(next_bottom);
        size_t next_index2=compo_list->index(next_sommit);

        if (next_index1==RW_NPOS)
        {
          next_index1=compo_list->entries()+1;
        }

        if (next_index2==RW_NPOS)
        {
          next_index2=compo_list->entries()+1;
        }

        if ((next_bottom.getVertex()!=UNDEF) && (next_index1<=next_index2))
        {
          interpol_dia=FALSE;
          next_index=compo_list->index(next_bottom);
          IntType nb_element=next_index-i;

          ValType dia_ratio=computeDiamsRatio(nb_element, bot_dia, next_bottom.getBotDia());

          top_dia=bot_dia/dia_ratio;

        }
        else
        {

          if (next_sommit.getVertex()!=UNDEF)
          {
            interpol_dia=FALSE;
            next_index=compo_list->index(next_sommit);

            IntType nb_element=next_index-i+1;

            ValType dia_ratio=computeDiamsRatio(nb_element, bot_dia, next_sommit.getTopDia());

            top_dia=bot_dia/dia_ratio;
          }
        }
      }

      if (top_dia==UNDEF)
      {
        // Same proportion

        top_dia=bot_dia*(father_top/father_bot);
      }
    }
    else
    {
      top_dia=br_element.getTopDia();
    }

 //    assert(bot_dia>0);
 //    assert(top_dia>0);

    if ((bot_dia<0) || (top_dia<0))
    {
      _areValidDiameters=FALSE;
    }

    compo_list->at(i).putBotDia(bot_dia);
    compo_list->at(i).putTopDia(top_dia);

    if (i==next_index)
    {
      interpol_dia=TRUE;
    }

  }
}


BranchElement Diameters::nextDefinedTopDia(const Branch& branch,
                                           const BranchElement start_element)
{
  BranchElement result(UNDEF);
  const BranchCompoList components=branch.branchComponents();
  IntType index=components.index(start_element);
  IntType nb_element=components.entries();
  IntType i=index;
  AmlBoolean end_of_loop=FALSE;

  while ((!end_of_loop) && (i<nb_element))
  {
    BranchElement current_element=components.at(i);

    if (current_element.getTopDia()!=UNDEF)
    {
      result=current_element;
      end_of_loop=TRUE;
    }

    i++;
  }

  return result;
}

BranchElement Diameters::nextDefinedBottomDia(const Branch& branch,
                                              const BranchElement start_element)
{
  BranchElement result(UNDEF);
  const BranchCompoList components=branch.branchComponents();
  IntType index=components.index(start_element);
  IntType nb_element=components.entries();
  IntType i=index;
  AmlBoolean end_of_loop=FALSE;

  while ((!end_of_loop) && (i<nb_element))
  {
    BranchElement current_element=components.at(i);

    if (current_element.getBotDia()!=UNDEF)
    {
      result=current_element;
      end_of_loop=TRUE;
    }

    i++;
  }

  return result;
}

ValType Diameters::computeDiamsRatio(IntType nb_element,
                                     ValType bot_dia,
                                     ValType top_dia)
{
  ValType result=pow(bot_dia/top_dia,1/(ValType)nb_element);

  return result;
}
