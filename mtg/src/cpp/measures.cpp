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
 *       $Id: measures.cpp 17611 2014-10-17 13:20:41Z pradal $
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
#include "aml/fnode.h"
//#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"
#include "tool/util_math.h"


#include "definitions.h"
#include "attributes.h"
#include "plant.h"
#include "coordinates.h"
#include "measures.h"

#include "dressingfile.h"
#include "defaultval.h"

#include "sam_msg.h"

using namespace std;

Measures::Measures(Plant* plant,
                   const FNode* function,
                   const ValType scale)
{
  _index=UNDEF;
  _scale=scale;
  _plant=plant;
  _level=UNDEF;
  _function=function;
  _mtg=plant->getMtg();
}

Measures::~Measures()
{
}

IntType Measures::lookForLevel(VId vertex)
{

  IntType result=UNDEF;

  // cette ligne montre que le calcul de _level
  // va correspondre au premier niveau a partir duquel
  // on va trouver un attribut pour l'objet Measures considere
  // si c'est un azimut ou un diametre, c'est pas mal.
  // mais ca ne marche pas si c'est des coordonnees spatiales
  // car la definition des coordonnees de la base du premier
  // segment se fait sur un complexe de ce segment.

  if (lookForFeature(vertex)==LUNDEF)
  {
    VIdList* list=_plant->compoSons(vertex);
    AmlBoolean end_of_loop=FALSE;
    IntType i=0;

    while ((i<list->entries()) && (!end_of_loop))
    {
      result=lookForLevel(list->at(i));

      if (result!=UNDEF)
      {
        end_of_loop=TRUE;
      }

      i++;
    }

    delete list;
  }
  else
  {
    result=_plant->vscale(vertex);
  }


  return result;
}


ValType Measures::lookForFeature(VId vertex, Date date) const
{
  const Feature* feature;

  IVal i;
  RVal r;
  ValType result=(ValType)LUNDEF;

  // cerr << "LookForFeature : vtx = " << vertex << ", _index = " << _index << endl;

  if (_function)
  {
    result=fnodeValue(vertex);
    // cerr << "A." << endl;
  }

  if (result==LUNDEF)
  {
    if ((_index==UNDEF) || (!_plant->hasFeatures(vertex)))
    {
      // cerr << "B." << endl;
      result=LUNDEF;
    }
    else
    {
      // cerr << "C." << endl;

      if (date != (unsigned long)LUNDEF) date=_plant->lastDate(vertex);

      feature=_plant->feature(vertex,_index,date);

      if (feature) {

        if ( _plant->fType(_index) == REAL) {

          // cerr << "E. " << endl;

          i=feature->i;

          IntType ii=(IntType) i;

          if (ii==LUNDEF)
            {
              // cerr << "F. " << endl;
              result=LUNDEF;

            }
          else {

            r=feature->r;

            // cerr << "FEATURE = " << r << endl;

            result=(ValType) r / (ValType)_scale;
          }

        }
        else {

          i=feature->i;

          IntType ii=(IntType) i;

          if (ii==LUNDEF)
            {
              result=LUNDEF;

            }
          else
            {
              result=(ValType) ii/ (ValType)_scale;
            }

        }

      }
    }
  }
  else
  {
    // cerr << "D." << endl;
    result=result/(ValType) _scale;
  }

  return result;
}

ValType Measures::fnodeValue(VId vertex) const
{

  assert(_function);

  ValType result=VAL_ERROR;

  AMObjVector argobjs(1); // Only one arg which is a vertex

  argobjs[0] = AMObj(AMObjType::VTX, vertex);

  AMObj result_obj = (*_function)(argobjs);

  switch(result_obj.tag()) {

  case  AMObjType::INTEGER:
    result = (ValType) result_obj.val.i;
    break;
  case  AMObjType::REAL:
    result = result_obj.val.r;
    break;
  default:
    //cerr << "Erreur !!" << endl;
    //cerr << "vtx  = " << vertex << endl;
    //cerr << "f(.) = " << result_obj << endl;
    result = LUNDEF;
  }

  assert(result!=VAL_ERROR);

  return result;
}

// Classe Category.

#define TRUNK_ORDER 0

Category::Category(Plant* plant,
                   const FNode* funct,
                   const DressingFile* dressing_file) : Measures(plant,funct,1)
{
  _dressingFile=dressing_file;

  // rechercher l'index

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_CATEGORY)
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

void Category::computeBranchCategory(Branch& branch)
{
  if (branch.getSupport()==UNDEF)
  {
    branch.putCategory(_dressingFile->getAxeDefaultCategory());
  }
  else
  {
    IntType category=lookForCategory(branch.baseOfBranch());

    if (category==LUNDEF)
    {
      // Calcule de l'ordre de ramification

      category=ramOrder(branch);
    }
    branch.putCategory(category);
  }
}


ValType Category::lookDownForCategory(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VIdList* sons_list=_plant->compoSons(vertex);

    if (!sons_list->isEmpty())
    {
      result=lookDownForCategory(sons_list->at(0));
    }

    delete sons_list;
  }

  return result;
}

ValType Category::lookUpForCategory(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VId father=_plant->compoFather(vertex);

    if (father!=UNDEF)
    {
      result=lookUpForCategory(father);
    }

  }

  return result;
}

IntType Category::lookForCategory(VId vertex) const
{
  ValType result=UNDEF;

  if (_level>_plant->vscale(vertex))
  {
    result=lookUpForCategory(vertex);
  }
  else
  {
    result=lookDownForCategory(vertex);
  }

  if (result==LUNDEF)
  {
    _dressingFile->getDefaultCategory();
  }

  return (IntType)result;
}


IntType Category::ramOrder(const Branch& branch)
{
  // Calcule l'ordre de ramification de la branche dont le premier element est
  // vertex.

  IntType result=0;

  VId support=branch.getSupport();

  if (support==UNDEF)
  {
    // Tronc de la plante.

    result=TRUNK_ORDER;
  }
  else
  {
    size_t nb_branches=_plant->nbBranches();
    size_t i=0;
    const Branch* the_branch=NULL;

    BranchElement skey (support);
    AmlBoolean end_of_loop=!(i<nb_branches);

    size_t index=RW_NPOS;

    while(!end_of_loop)
    {
      const Branch& br=_plant->findBranch(i);
      const BranchCompoList& brcl=br.branchComponents();

      if (brcl.contains(skey))
      {
        end_of_loop=TRUE;
        index=i;
        the_branch=&br;
      }
      else
      {
        i++;
        end_of_loop=!(i<nb_branches);
      }
    }

    assert(index!=RW_NPOS);

    result=1+ramOrder(*the_branch);
  }

  return result;
}


// Classe Azimut


Azimut::Azimut(Plant* plant,
               const FNode* funct,
               ValType base,
               ValType scale=180/M_PI):Measures(plant,funct,scale)

     // The azumt is given in degrees, so the scale must transform it in radians.
{
  _base=base/scale;
  _isPosition=FALSE;
  _isAzimut=FALSE;

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_AZIMUT)
    {
      _isAzimut=TRUE;
      _index=i;
    }
  }

  VId root=_plant->mtgRoot();

  if (_index!=UNDEF)
  {
    _level=lookForLevel(root);
  }

}

Azimut::Azimut(Plant* plant,
               const FNode* funct,
               ValType nb_tours,
               ValType nb_leaves,
               ValType scale):Measures(plant,funct,scale)
{
  _base=nb_tours*2*M_PI/nb_leaves;
  _isPosition=FALSE;
  _isAzimut=FALSE;
  _nbTours=nb_tours;

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_POSITION)
    {
      _isPosition=TRUE;
      _index=i;
    }
  }

  VId root=_plant->mtgRoot();

  if (_index!=UNDEF)
  {
    _level=lookForLevel(root);
  }
}


ValType Azimut::lookUpForAzimut(VId vertex) const
{
  ValType result=LUNDEF;

  result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VId father=_plant->compoFather(vertex);

    if (father!=UNDEF)
    {
      result=lookUpForAzimut(father);
    }
  }

  return result;
}

ValType Azimut::lookDownForAzimut(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VId detailed_relation=_plant->location(vertex);

    if (_plant->vscale(detailed_relation)>_plant->vscale(vertex))
    {
      VId father=_plant->topoFather(vertex,ANY);

      EType edge=_plant->edgeType(father,vertex);

      VIdList* list=_plant->topoSons(detailed_relation,edge);

      IntType i=0;
      AmlBoolean end_of_loop=FALSE;
      VId the_vertex=UNDEF;

      while ((i<list->entries()) && (!end_of_loop))
      {
        if (_plant->compoFather(list->at(i))==vertex)
        {
          end_of_loop=TRUE;
          the_vertex=list->at(i);
        }

        i++;
      }

      delete list;

      if (the_vertex!=UNDEF)
      {
        result=lookForFeature(the_vertex);
      }

      if (result==LUNDEF)
      {
        result=lookUpForAzimut(detailed_relation);
      }
    }
  }

  return result;
}


ValType Azimut::lookForAzimut(VId vertex) const
{
  ValType result=LUNDEF;
  ValType index=LUNDEF;

  if (_plant->vscale(vertex)>=_level)
  {
    index=lookUpForAzimut(vertex);

  }
  else
  {
    index=lookDownForAzimut(vertex);

  }

  if (index!=LUNDEF)
  {
    if (_isPosition)
    {
      result=_base*index;
    }
    if (_isAzimut)
    {
      result=index;
    }
  }

  return result;
}

void Azimut::computeAzimut()
{
  size_t n=_plant->nbBranches();
  
  for(size_t i=0;i<n;i++)
  {
    Branch* branch=_plant->_branches->at(i);
    BranchCompoList* list=branch->_components;
    IntType plant_id=branch->_plantNumber;
    size_t nb_components=list->entries();

    ValType beta=0;
	
    for(size_t j=0;j<nb_components;j++)
    { 
	  
      VId vertex=list->at(j).getVertex();
	  
      Branch* object=new Branch (vertex,plant_id);

      size_t occurrences=_plant->_branches->occurrencesOf(object);
      size_t index=_plant->_branches->index(object);
      if (index!=RW_NPOS)
      {
		for(size_t k=index;k<occurrences+index;k++)
		{
		  VId first_element=_plant->_branches->at(k)->baseOfBranch();
		  
		  ValType azimut=lookForAzimut(first_element);
		  
		  if (azimut!=LUNDEF)
		  {
			_plant->_branches->at(k)->_components->at(0).putBeta(azimut);
			
			// On remet a jour la philotaxie par rapport aux informations fournies.
			
			beta=azimut;
		  }
		  else
		  {
			_plant->_branches->at(k)->_components->at(0).putBeta(beta);
			
			// Dans ce cas on incremente la phyllotaxie.
			
			beta+=_base;
		  } 
		  
		  
		}
      }
	  
      delete object;
    }
  }
}


Alpha::Alpha(Plant* plant,
             const FNode* funct,
             const DressingFile* dressing_file,
             ValType scale=180/M_PI) : Measures(plant,funct,scale)
{
  _defaultAlpha=dressing_file->getDefaultAlpha()/scale;

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_ALPHA)
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

void Alpha::computeBranchAlpha(Branch& branch)
{
  VId vertex=branch.baseOfBranch();

  ValType angle=computeElementAngle(vertex);

  branch._alpha=angle;
}


ValType Alpha::computeElementAngle(VId vertex) const
{
  ValType result=LUNDEF;

  result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    if (_plant->vscale(vertex)>=_level)
    {
      result=lookUpForAlpha(vertex);

      if (result==LUNDEF)
      {
        result=lookDownForAlpha(vertex);
      }
    }
  }


/*  if (result==LUNDEF)
  {
    result=_defaultAlpha;
  }
*/
  return result;
}

ValType Alpha::lookUpForAlpha(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VId compo_father=_plant->compoFather(vertex);

    if (compo_father!=UNDEF)
    {
      VIdList* list_of_brothers=_plant->compoSons(compo_father);

      if (list_of_brothers->at(0)==vertex)
      {
        result=lookUpForAlpha(compo_father);
      }

      delete list_of_brothers;
    }
  }

  return result;
}

ValType Alpha::lookDownForAlpha(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VIdList* list_of_sons=_plant->compoSons(vertex);

    if (!list_of_sons->isEmpty())
    {
      VId son=list_of_sons->at(0);
      result=lookDownForAlpha(son);
    }

    delete list_of_sons;
  }

  return result;

}


Teta::Teta(Plant* plant,
           const FNode* funct,
           const DressingFile* dressing_file,
           ValType scale=180/M_PI) : Measures(plant,funct,scale)
{
  _default=dressing_file->getDefaultTeta()/scale;

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_TETA)
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

ValType Teta::computeTeta(VId vertex) const
{
  ValType result=LUNDEF;

  result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    if (_plant->vscale(vertex)>=_level)
    {
      result=lookUp(vertex);

      if (result==LUNDEF)
      {
        result=lookDown(vertex);
      }
    }
  }

  if (result==LUNDEF) result=_default;

  return result;
}


ValType Teta::lookUp(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VId compo_father=_plant->compoFather(vertex);

    if (compo_father!=UNDEF)
    {
      VIdList* list_of_brothers=_plant->compoSons(compo_father);

      if (list_of_brothers->at(0)==vertex)
      {
        result=lookUp(compo_father);
      }

      delete list_of_brothers;
    }
  }

  return result;
}

ValType Teta::lookDown(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VIdList* list_of_sons=_plant->compoSons(vertex);

    if (!list_of_sons->isEmpty())
    {
      VId son=list_of_sons->at(0);
      result=lookDown(son);
    }

    delete list_of_sons;
  }

  return result;

}


Phi::Phi(Plant* plant,
           const FNode* funct,
           const DressingFile* dressing_file,
           ValType scale=180/M_PI) : Measures(plant,funct,scale)
{
  _default=dressing_file->getDefaultPhi()/scale;

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_PHI)
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

ValType Phi::computePhi(VId vertex) const
{
  ValType result=LUNDEF;

  result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    if (_plant->vscale(vertex)>=_level)
    {
      result=lookUp(vertex);

      if (result==LUNDEF)
      {
        result=lookDown(vertex);
      }
    }
  }

  if (result==LUNDEF) result=_default;

  return result;
}


ValType Phi::lookUp(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VId compo_father=_plant->compoFather(vertex);

    if (compo_father!=UNDEF)
    {
      VIdList* list_of_brothers=_plant->compoSons(compo_father);

      if (list_of_brothers->at(0)==vertex)
      {
        result=lookUp(compo_father);
      }

      delete list_of_brothers;
    }
  }

  return result;
}

ValType Phi::lookDown(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VIdList* list_of_sons=_plant->compoSons(vertex);

    if (!list_of_sons->isEmpty())
    {
      VId son=list_of_sons->at(0);
      result=lookDown(son);
    }

    delete list_of_sons;
  }

  return result;

}


Psi::Psi(Plant* plant,
           const FNode* funct,
           const DressingFile* dressing_file,
           ValType scale=180/M_PI) : Measures(plant,funct,scale)
{
  _default=dressing_file->getDefaultPsi()/scale;

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_PSI)
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

ValType Psi::computePsi(VId vertex) const
{
  ValType result=LUNDEF;

  result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    if (_plant->vscale(vertex)>=_level)
    {
      result=lookUp(vertex);

      if (result==LUNDEF)
      {
        result=lookDown(vertex);
      }
    }
  }

  if (result==LUNDEF) result=_default;

  return result;
}


ValType Psi::lookUp(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VId compo_father=_plant->compoFather(vertex);

    if (compo_father!=UNDEF)
    {
      VIdList* list_of_brothers=_plant->compoSons(compo_father);

      if (list_of_brothers->at(0)==vertex)
      {
        result=lookUp(compo_father);
      }

      delete list_of_brothers;
    }
  }

  return result;
}

ValType Psi::lookDown(VId vertex) const
{
  ValType result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VIdList* list_of_sons=_plant->compoSons(vertex);

    if (!list_of_sons->isEmpty())
    {
      VId son=list_of_sons->at(0);
      result=lookDown(son);
    }

    delete list_of_sons;
  }

  return result;

}


// Classe length


Length::Length(Plant* plant,
               const DressingFile* dressing_file,
               const FNode* length_function,
               const ValType scale=1):Measures(plant,length_function,scale)
{
  _dressingFile=dressing_file;
  _areValidLengths=TRUE;

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_LENGTH)
    {
      _index=i;
    }
  }

  VId root=_plant->mtgRoot();

  if (_index!=UNDEF)
  {
    _level=lookForLevel(root);
  }

  // cerr << "Nb de features :" << _plant->featureNb() << endl;

  // cerr << "A la construction d'un objet Length, _index vaut : " << _index << endl;

}

void Length::computeBranchLengths(Branch& branch, Measures*)
{
  IntType nb_element=branch._components->entries();

  for(IntType i=0;i<nb_element;i++)
  {
    computeElementLength(branch._components->at(i));
  }
}


void Length::computeElementLength(BranchElement& the_element)
{

  VId vertex=the_element.getVertex();
  ValType result=VAL_ERROR;

  if (_plant->vscale(vertex)>=_level)
  {
    result=lookUp(vertex);

    if (result==LUNDEF)
    {

      result=lookDown(vertex);
    }
  }
  else
  {

    result=lookDown(vertex);
  }

  // assert((result!=VAL_ERROR) && (result>0));

  if ((result==VAL_ERROR) || (result<=0))
  {
    _areValidLengths=FALSE;
  }

  the_element.putLength(result);

}


// Protected methods.


ValType Length::lookDown(const VId vertex) const
{
  ValType result=LUNDEF;

  result=lookForFeature(vertex);

  if (result==LUNDEF)
  {
    VIdList* list=_plant->compoSons(vertex);

    if (list->entries()!=0)
    {
      ValType length=0;

      for (size_t i=0;i<list->entries();i++)
      {
        VId v=list->at(i);
        length+=lookDown(v);
      }

      delete list;
      result=length;

    }
    else
    {
      char a_symb=_plant->symbol(vertex);
      result=_dressingFile->getMinLength(a_symb);
    }
  }


  return result;
}

ValType Length::lookUp(const VId vertex) const
{
  ValType result=LUNDEF;
  VId father;

  result=lookForFeature(vertex);

  if ((result==LUNDEF) &&
      (_plant->vscale(vertex)>=1))
  {
    father=_plant->compoFather(vertex);
    result=lookUp(father);

    if (result!=LUNDEF)
    {
      result/=(ValType)(_plant->compoSons(father)->entries());
    }
  }

  return result;
}


// Classe CoordLength


IndexSegment::IndexSegment()
{
  topIndex=-1;
  botIndex=-1;
}

IndexSegment::IndexSegment(IntType bot, IntType top)
{
  topIndex=top;
  botIndex=bot;
}

void IndexSegment::modif(IntType i)
{
  botIndex=topIndex;
  topIndex=i;
}

const IndexSegment& IndexSegment::operator=(IndexSegment& ind_s)
{

  if (this!=&ind_s)
  {
    topIndex=ind_s.topIndex;
    botIndex=ind_s.botIndex;
  }

  return *this;
}

// Membres de la classe CoordLength.

CoordLength::CoordLength(Plant* plant,
                         RWCString length_algo,
                         const FNode* funct,
                         const DressingFile* dressing_file,
                         ValType scale=1):Measures(plant,funct,scale)
{

  _dressingFile=dressing_file;
//  assert(_dressingFile!=NULL);
  _length=new Length (_plant,_dressingFile,funct,_dressingFile->getLengthUnit());
  _isValid=TRUE;
  _function=funct;

  _length_algo = length_algo;

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==ATT_LENGTH)
    {
      _index=i;
    }
  }

  //assert(_index!=UNDEF);

  VId root=_plant->mtgRoot();

  if (_index!=UNDEF)
    _level=lookForLevel(root)+1;
  {
    _isValid=TRUE;
  }

  //_lastIndex=0;
}


CoordLength::~CoordLength()
{
  delete _length;
}


// Cette methode est appelee par le geomcomputer (avant l'appel du calcul des
// coordonnees.  elle precalcule les longueurs de segments de la branche.
//
// Cette methode utilise ou non l'heuristique des index: la longueur d'un
// segment est proportionnelle a la progression de son index par rapport
// a son pere dans le segment englobant dont les coordonnees sont definies.
//
// Cette heuristique ne s'applique qu'AVANT le dernier vertex renseigne :
// AVANT, toute fonction donnant la longueur et la direction d'un segment
// est invalidee (pb de coherence d'une information specifiee 2 fois
// par de moyens differents
//
// APRES, les memes fonctions deviennent operantes, puisqu'il n'y a plus de
// specification de ces grandeurs via une possible interpolation lineaire
// entre deux points.
//
// Ceci est pris en compte dans la fonction ci dessous en calculant un ratio
// correspondant a la valeur dont il faudra diviser la longueur du
// segment englobant pour obtenir la longueur d'une entite. Cette valeur
// n'est valide que pour les composants de la branche se situant avant
// le dernier point renseigne.
//
// Si cette heuristique n'est pas prise en compte, la longueur d'un segment
// sans coordonnees sera inversement proportionnelle au nombre de segments
// entre deux points donnes ayant des cordonnees.
//
// en plus il existe 2 manieres de traiter le premier index d'une branche
// par rapport a l'index du porteur. Soit on considere qu'on redemarre a 0
// et que l'index du premier element est le delta d'index depuis la branche,
// soit, on considere qu'on redemarre a l'index du porteur de cette branche.


void CoordLength::computeBranchLengths(Branch& branch, Measures* coordobj)
{
  AmlBoolean is_coords= isThereCoords(branch, coordobj);

  // cerr << "*** CoordLength::computeBranchLengths" << endl;
  // cerr << "\tCalcul des LONGUEURS des entites de la branche " << endl;

  if (_isValid)
  {

    if (!is_coords)
    {
      // cerr << "\t->branch Standard" << endl;

      // S'il n'y a pas de coordonnees on appel un
      // objet traitant des branches standards (sans coordonnees).
      // (_length est de type Length)
      // le deuxieme argument ne sert a rien dans ce cas la.
      _length->computeBranchLengths(branch, 0);
    }
    else
    {

      // On utilise une heuristique sur l'index des composants pour calculer
      // la longueur du composant. A cette etape on determine juste un ratio
      // pour l'element qui est un facteur de division (de val abs > 1)
      // qui servira a prendre une proportion de la distance totale
      // definie entre les deux plus proches composants sur l'axe
      // encadrant ce segment pour lesquels les coordonnees sont renseignees.

      // remarque IMPORTANTE : dans le cas ou on utilise cette heuristique
      // on ne tient pas compte d'une definition explicite eventuelle de
      // la longueur (comme attribut d'un MTG ou definit par une fonction
      // utilisateur. Ceci introduirait une inhomogeneite de la definition
      // des longueurs qui pourrait donner lieu a des incoherences importantes
      // dans le calcul de la geometrie.


      // cerr << "\t->branch avec des coordonnees" << endl;
      size_t nb_elements=branch._components->entries();

      // initial_index est l'index initial de la branche:
      // c'est soit l'index du support soit 0

      IntType initial_index=0;

      if (_length_algo == "UseIndexes")
      {

        // Option pour interpreter l'index du premier vertex de la branche
        // demande par l'utilisateur: dans le cas ou l'index du premier vertex
        // est superieur a celui de son porteur: faire comme si la longueur de
        // ce vertex etait proportionnelle a la difference d'index avec le
        // porteur dans le segment compris entre le porteur et le premier vertex
        // renseigne de cet axe

        IntType support_index =  -1;
        IntType first_index = -1;

        // On recherche l'index du support.

        VId first_branch_vtx = branch._components->at(0).getVertex();
        VId support=_plant->topoFather(first_branch_vtx, ANY);

        if (first_branch_vtx != UNDEF) {
          first_index = _plant->vindex(first_branch_vtx);
        }
        if (support != UNDEF) {
          support_index = _plant->vindex(support);
        }

        // Dans le cas ou l'index est croissant en passant du porteur
        // au porte, on considere que l'index du porte correspond a
        // une longueur relative par rapport a l'index du porteur
        // sinon, l'index du porte est une longueur absolue depuis le porteur
        // (initial_index == 0)

        if (support_index != -1 &&
            support_index < first_index) {
          initial_index = support_index;
        }

      }
      // Else the index is reset at the beginning of each axis
      //  initial_index=0;

      // Calcul du tableau des index cumules
      // l'index cumule sert a tenir compte du fait que normalement
      // les index doivent etre croissants. Lorsqu'ils decroissent
      // il faut faire comme si ils etaient croissants
      // exemple:
      // indexes reels  : 1   3   12   4   6   9   15   33   1   6
      // indexes cumules: 1   3   12  16  18  21   27   45   46 52

      int* cum_index_array = new int[nb_elements];

      int index;
      int previous_index = initial_index;
      int previous_cum_ref_index = 0;

      VId vertex;

      for(size_t i1=0;i1<nb_elements;i1++)
      {         

	vertex = branch._components->at(i1).getVertex();
	index = _plant->vindex(vertex); 
	
	assert(index >=0);

	if (index < previous_index && i1 > 0) { // decroissance de l'index
	  // si i == 0, c'est que previous_index = initial_index ==
	  // support_index et qu'on a une decroissance d'index en passant sur du
	  // porteur au porte. Et il ne faut rien faire puisque
	  // previous_cum_ref_index = 0 et c'est Ok.

	  previous_cum_ref_index = cum_index_array[i1-1];

	}
	
	cum_index_array[i1] = previous_cum_ref_index + index;

	previous_index = index;

      }

      /*

      cerr << "branch indexes : ";
      for(i=0;i<nb_elements;i++)
      {
        cerr << _plant->vindex(branch._components->at(i).getVertex()) << " ";
      }
      cerr << endl;
      cerr << "cumul  indexes : ";
      for(i=0;i<nb_elements;i++)
      {
        cerr << cum_index_array[i] << " ";
      }
      cerr << endl;

      */

      // Dans tous les cas, le support est considere comme etant renseigne.
      // On recherche le prochain element ayant des coordonnees.
      // on recupere d'abord le rang du prochain vtx ayant des coordonnees
      // dans la branche

      // start search at rank 0 in the branch element list
      int rank_next_vtx_with_coord = nextIndex(branch,0, coordobj);
      assert(rank_next_vtx_with_coord!=-1);

      // cerr << "rank of the first vertex with features = "
      // << rank_next_vtx_with_coord << endl;

      VId next_vtx_with_coord = branch._components->at(rank_next_vtx_with_coord).getVertex();

      // next_vtx_with_coord ne doit pas etre a UNDEF, puisqu'il y a au moins
      // un element contenant des coordonnees sur cette branche.

      IntType next_index_with_coord = cum_index_array[rank_next_vtx_with_coord];

      // cerr << "next_index_with_coord = " << next_index_with_coord << endl;

      // on cree le premier intervalle correspondant a deux vertex consecutifs
      // renseignes (entre le support et le premier vertex renseigne de l'axe)

      IndexSegment current_segment(initial_index, next_index_with_coord);

      // cerr << "segment : [" << current_segment.botIndex << ","
      // << current_segment.topIndex << "]" << endl;


      // Puis, on cree tous les autres intervalles (constitues des index
      // (cumules) des autres vertex ayant des coordonnees sur cette branche

      // c'est le support qui est le previous vtx with coords (rang = -1)
      IntType rank_prev_vtx_with_coord = -1;

      for(size_t i=0;i<nb_elements;i++)
      {         
	vertex = branch._components->at(i).getVertex();
	index = _plant->vindex(vertex);
	
	// recupere le rang du prochain vertex ayant des coordonnees
	int next_i=nextIndex(branch,i,coordobj);

	if ((next_i!=RW_NPOS) && (next_i!=rank_next_vtx_with_coord)) 
	{

	  rank_prev_vtx_with_coord=rank_next_vtx_with_coord;
	  rank_next_vtx_with_coord=next_i;

	  next_index_with_coord= cum_index_array[next_i] ;
	  current_segment.modif(next_index_with_coord);


	}
	
	ValType length;

	// A-t-on passe le dernier point renseigne de l'axe ?
	if (next_i!=RW_NPOS) {

	  if (_length_algo == "UseAxisIndexes" ||
	      _length_algo == "UseIndexes") { // METTRE LA L"OPTION UTILISATEUR ICI !!!!!!

	    // heuristique utilisant l'index

	    length =computeElementLength(vertex,
					 cum_index_array[i], // index courant (cumule)
					 i>0 ? cum_index_array[i-1]: initial_index,
					 current_segment);   // intervalle courant
	  }
	  else {
	    // Heuristique pour une repartition homogene des longueurs
	    // entre deux points renseignes.
	    // cette formule donne le ratio qui definira la longueur
	    // des composants de cette plage de facon homogene.
	    // elle marche meme si on est au debut de la branche
	    // (i.e. rank_prev_vtx_with_coord = -1)

	    // cerr << "prev_r = " << rank_prev_vtx_with_coord << " , next_r = " << rank_next_vtx_with_coord << endl;
	    // cerr << "Ratio = " << rank_next_vtx_with_coord - rank_prev_vtx_with_coord << endl;

	    length = (ValType)(rank_next_vtx_with_coord - rank_prev_vtx_with_coord);

	  }

	}
	else {
	  
	  // Si on a passe le dernier point renseigne de l'axe, on met une
	  // valeur negative qui ne devra pas etre utilisee
	  length = -1; 

	}

	// cerr << "\tVertex " << vertex 
	// << ": Ratio de LONGUEUR STOCKEE = " << length << endl;

	branch._components->at(i).putLength(length);

      }

      delete [] cum_index_array;

    }
  }

  // cerr << "*** End CoordLength::computeBranchLengths" << endl;

}

AmlBoolean CoordLength::isThereCoords(Branch& br, Measures* coordobj)
{
  // Verifie s'il y a des coordonnees renseignees dans cette branche.

  AmlBoolean result=FALSE;
  size_t nb_elements=br._components->entries();
  size_t i=0;
  AmlBoolean end_of_loop= (result) ||
                       (i>=nb_elements);

  RequiredCoords* coords = (RequiredCoords*)coordobj;

  // cerr << "_level = " << _level << endl;

  ValType l1=0,l2=0,l3=0;
  MyVector vec;

  while (!end_of_loop)
  {

    VId vertex=br._components->at(i).getVertex();

    /*
    cerr << "coords: " << endl;
    cerr << "\tcoords->_xcoord->_index" <<coords->_xcoord->_index <<  endl;
    cerr << "\tcoords->_ycoord->_index" <<coords->_ycoord->_index <<  endl;
    cerr << "\tcoords->_zcoord->_index" <<coords->_zcoord->_index <<  endl;
    */

    if ( (coords->findFeature(vertex,coords->_xcoord->_index,l1) &&
          coords->findFeature(vertex,coords->_ycoord->_index,l2) &&
          coords->findFeature(vertex,coords->_zcoord->_index,l3)))
      {
        if (coords->_refSystem->findPoint(l1,l2,l3,vec)) {
          result=TRUE;
        }
        else
          {
            i++;
          }
      }
    else
      {
        i++;
      }


    end_of_loop=(result) ||  (i>=nb_elements);
  }

  return result;
}


// Calcule le prochain vertex a partir de i compris ayant des coordonnees.
// l'index cumule au niveau de i est passe par reference en argument
// et est mis a jour le cas echeant.
// - br designe la branche consideree
// - i represente l'indice initial a partir duquel on cherche le prochain element renseigne
// - coordobj donne le moyen d'evaluer si les coordonnees trouvees sont valides ou non

int CoordLength::nextIndex(Branch& br, size_t i, Measures* coordobj)
{

  // Recherche le prochain element de la plante contenant des coordonnees.
  // On commence la recherche a partir de l'element d'index i (compris)

  int result=RW_NPOS;
  size_t nb_elements=br._components->entries();

  AmlBoolean end_of_loop=(i==RW_NPOS);

  MyVector vec;
  ValType l1=0,l2=0,l3=0;
  RequiredCoords* coords = (RequiredCoords*)coordobj;

  while (!end_of_loop)
  {

    VId vertex = br._components->at(i).getVertex();

    if (  (coords->findFeature(vertex,coords->_xcoord->_index,l1) &&
           coords->findFeature(vertex,coords->_ycoord->_index,l2) &&
           coords->findFeature(vertex,coords->_zcoord->_index,l3)))
      {
        if (coords->_refSystem->findPoint(l1,l2,l3,vec)) {
          // cerr << "i = " << i <<  ", LookForFeature("<< vertex << ") = " << lookForFeature(vertex) << endl;
          result=i;
          end_of_loop=TRUE;
        }
        else
          {
            i++;
            end_of_loop=(i>=nb_elements);
          }
      }
    else
      {
        i++;
        end_of_loop=(i>=nb_elements);
      }
  }

  return result;
}

ValType CoordLength::getMinLength(VId vertex) const {
  if(_dressingFile == NULL)return DEFAULT_MIN_LENGTH;
  return _dressingFile->getMinLength(_plant->symbol(vertex));
}


// Calcul un ratio qui servira a determiner la longueur de l'element passe
// en argument ulterieurement
// - vertex = element considere
// - cumulated_index : index cumule de ce vertex depuis le debut de la branche (cf plus haut)
// - cumulated_previous_index: index cumule du vertex immediatement precedent
//   sur l'axe
// - ind_s = [b,t] ou b et t sont respectivement les index cumules
//   des deux vertex delimitant le segment
//   auquel vertex appartient dont les vertex interieurs n'ont pas
//   de coordonnees renseignees valides
//   et dont les vertex extremites ont des coordonnees renseignees valides.
//
// Supposons par exemple que cumulated index = 11,
// et que ind_s = [5,23]
// alors le ratio retourne sera (23-5) / (11-5) = 18/6 = 3
// c'est a dire que le vertex se situe (si l'on en juge par son index!) a un tiers de la distance
// entre les vertex d'index cumule 5 et 23.

ValType CoordLength::computeElementLength(VId vertex,
                                          IntType cumulated_index,
                                          IntType cumulated_previous_index,
                                          IndexSegment ind_s)

{
  ValType result=VAL_ERROR;

  // Deux cas peuvent se presenter:
  // Si next_index==-1 Alors on appliquera une regle de trois pour le calcul de la longueur
  // Sinon ind_s contient les index du segment dans lequel on se trouve.

  /*
   cerr << "CoordLength::computeElementLength" << endl;
   cerr << "\tvertex = " << vertex << ", bot index = "
   << ind_s.botIndex << ", top index = " << ind_s.topIndex << endl;
  */

  IntType big_delta_index=ind_s.topIndex-ind_s.botIndex; // difference des index *cumules*

  if (cumulated_index == 0) {

    // il s'agit du premier index de la branche qui est 0
    // on met un ratio infini pour que la taille du segment soit de 0

    result = MAXFLOAT;

  }
  else {

    /*
    cerr << "\tcumulated_index = " << cumulated_index << endl;
    cerr << "\tcumulated_previous_index = " << cumulated_previous_index << endl;
    */

    IntType delta_index=cumulated_index-cumulated_previous_index;

    if ((delta_index==0) || (big_delta_index==0))
    {
      result= MAXFLOAT;
      cout << APPL_MSG[INDEX_WARNING] << " At vertex : " << vertex
           << ": Length is NULL" << endl;
    }
    else
    {
      result=(ValType) big_delta_index/(ValType)delta_index;

      // cerr << "\tresult = " << (ValType) big_delta_index
      // << "/" << (ValType)delta_index << " = " << result << endl;
    }
  }

  if (result<1)
  {
    /*
    cerr << "\tcumulated_index = " << cumulated_index << endl;
    cerr << "\tcumulated_previous_index = " << cumulated_previous_index << endl;

    cerr << "\tratio = " << (ValType) big_delta_index
         << "/" << (ValType)(cumulated_index-cumulated_previous_index) << " = "
         << result << endl;
    */

    result=_dressingFile->getMinLength(_plant->symbol(vertex));

    cout << APPL_MSG[INDEX_WARNING2] << " At vertex : "
         << vertex << ": Length is default length (see DressingFile)" << endl;

  }
  // cerr << "*** End CoordLength::computeElementLength" << endl;

  return result;
}


L1Coord::L1Coord(Plant* plant,
                 const FNode* funct,ValType scale):Measures(plant,funct,scale)
{
  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==TR_X)
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

L2Coord::L2Coord(Plant* plant,
                 const FNode* funct, ValType scale):Measures(plant,funct,scale)
{
  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==TR_Y)
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

L3Coord::L3Coord(Plant* plant,
                 const FNode* funct,ValType scale):Measures(plant,funct,scale)
{
  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==TR_Z)
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

// For cartesian coordinates

XCoord::XCoord(Plant* plant,
               const FNode* funct,ValType scale):Measures(plant,funct,scale)
{
  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==CA_X)
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

YCoord::YCoord(Plant* plant,
               const FNode* funct,ValType scale):Measures(plant,funct,scale)
{
  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==CA_Y)
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

ZCoord::ZCoord(Plant* plant,
               const FNode* funct,ValType scale):Measures(plant,funct,scale)
{
  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==CA_Z)
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


















