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
 *       $Id: plant.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "plant.h"

using namespace std;

LongType Branch::_branchCounter=0;
LongType Plant::_plantNumber=0;
IntType Plant::_plantCounter=0;

Plant::Plant(MTG* mtg,
             PlantFrame* plantframe,
             VId vertex,
             EType default_edge,
             IntType l,
             Options opt=NORMAL,
             ValType* translation,
             ValType* origin
)

{
  _mtg=mtg;
  _branches=new Ramifications;
  _myTree=new MyTree;
  _defaultEdge=default_edge;
  _components=new VIdList;
  _plantId=_plantNumber;
  _isSympodial=(opt==SYMPODIAL);

  _root_list = NULL;

  _plantframe = plantframe;

  if (translation)
  _translation = new MyVector(translation[0],
                              translation[1],
                              translation[2]);
  else _translation = 0;

  _origin = origin;

  if (mtg->existsVertex(vertex))
  {

    IntType level=l;
    _vertex=vertex;
    if (level==-1)
    {
      level=_mtg->vscale(vertex)+1;
    }
    _level=level;

    _components=lookForComponents(vertex,level);

    if (_components->entries()!=0)
    {
      if (!_isSympodial)
      {
        buildMyTree();
      }
      else
      {
        buildSympodialTree();
      }

      VIdList* list=theRoots(vertex,level);

      size_t nb=list->entries();


      // testSons();

      // cout << "PlantFrame d'un Vertex: avant la boucle ...." << endl;

      for(size_t i=0;i<nb;i++)
      {
        // cout << "TREATMENT OF ROOT : " << list->at(i) << endl;
        lookForBranches(list->at(i));
      }

      // cout << "PlantFrame d'un Vertex: apres la boucle ...." << endl;
      delete list;
      _isValid=TRUE;

    }
    else
    {
      cerr << "No components found to compute the geometry of vertex " << vertex << " ..." << endl;
      _isValid=FALSE;
    }
  }
  else
  {
    cerr << "The vertex " << vertex << " in the argument list is not a valid vertex" << endl;
    _isValid=FALSE;
  }


  _maxpoint=MyVector(-MAX_VALTYPE,-MAX_VALTYPE,-MAX_VALTYPE);
  _minpoint=MyVector(MAX_VALTYPE,MAX_VALTYPE,MAX_VALTYPE);


}


Plant::Plant(MTG* mtg,
             PlantFrame* plantframe,
             const VIdList* list_of_vertex,
             EType default_edge,
             IntType l,
             Options opt=NORMAL,
             ValType* translation,
             ValType* origin
)

{
  _mtg=mtg;
  _branches=new Ramifications;
  _myTree=new MyTree;
  _defaultEdge=default_edge;
  _components=new VIdList;
  _plantId=_plantNumber;
  _isSympodial=(opt==SYMPODIAL);
  _root_list = NULL;

  _plantframe = plantframe;

  if (translation)
  _translation = new MyVector(translation[0],
                              translation[1],
                              translation[2]);
  else _translation = 0;

  _origin = origin;


  VId vertex;

  if (!list_of_vertex->isEmpty())
  {
    vertex=list_of_vertex->at(0);
  }
  else
  {
    vertex=UNDEF;
  }

  if (mtg->existsVertex(vertex))
  {

    IntType level=l;
    _vertex=vertex;
    if (level==-1)
    {
      level=_mtg->vscale(vertex)+1;
    }
    _level=level;

    _components=lookForComponents(list_of_vertex,level);

    if (_components->entries()!=0)
    {
      if (!_isSympodial)
      {
        buildMyTree();
      }
      else
      {
        buildSympodialTree();
      }

      _root_list=theRoots(vertex,level);

      size_t nb=_root_list->entries();

      // cerr << "root list nb = " << nb << endl;

      for(size_t i=0;i<nb;i++)
      {
        // cerr << "_root_list->at(" << i << ")  = " << _root_list->at(i) << " " << endl;

        lookForBranches(_root_list->at(i));

        /*
        cerr << "(";
        cerr << _origin[3*i] << ",";
        cerr << _origin[3*i+1] << ",";
        cerr << _origin[3*i+2] << ") ";
        cerr << flush;
        */

      }

      //cerr << endl;

      _isValid=TRUE;

    }
    else
    {
      cerr << "No components found to compute the geometry of vertex " << vertex << " ..." << endl;
      _isValid=FALSE;
    }
  }
  else
  {
    cerr << "The vertex " << vertex << " in the argument list is not a valid vertex" << endl;
    _isValid=FALSE;
  }

  _maxpoint=MyVector(-MAX_VALTYPE,-MAX_VALTYPE,-MAX_VALTYPE);
  _minpoint=MyVector(MAX_VALTYPE,MAX_VALTYPE,MAX_VALTYPE);


}

Plant::~Plant()
{
  if (_translation) delete _translation;

  if (_root_list) delete _root_list;

  // was created before calling the constructor of a plantframe
  if (_origin) delete [] _origin;

  _branches->clearAndDestroy();
  delete _branches;
  delete _components;
  _myTree->clearAndDestroy();
  delete _myTree;
}

AmlBoolean Plant::operator==(const Plant& plant) const
{
  AmlBoolean result=0;

  if (_plantId==plant._plantId)
  {
    result=TRUE;
  }

  return result;
}


MTG* Plant::getMtg()
{
  return _mtg;
}

const MTG* Plant::getMtg() const
{
  return _mtg;
}



const Branch& Plant::findBranch(size_t index) const
{
  assert((index<_branches->entries()));

  return *_branches->at(index);
}


// Private methods

// builds the branches corresponding to the branching system
// starting at vertex origin.

void Plant::lookForBranches(VId origin)
{
  RWTQueue<VId,VIdList> vqueue;
  BranchElement* branch_element;
  Branch* branch;
  VIdList* list_of_topo_sons;
  VId vertex;

  if (topoFather(origin,ANY) == UNDEF )
  {
   _plantCounter++;
  }

  branch=new Branch (topoFather(origin,ANY),_plantCounter);

  branch_element=new BranchElement (origin);

  branch->addElement(*branch_element);

  AmlBoolean end_of_loop=FALSE;

  while (!end_of_loop)
  {

    list_of_topo_sons=sons(origin,LESS);

    /*
    VIdListIter next(*list_of_topo_sons);

    cout << "LESS SONS of " << origin << ": ";
    while (next()) {

      cout << next.key() << " " ;
    }
    cout << endl;

    cout << "step2" << endl;
    */

    if (list_of_topo_sons->entries()==0)
    {
      end_of_loop=TRUE;
    }
    //cout << "Number of LESS topo_sons : " << list_of_topo_sons->entries() << endl;

    delete list_of_topo_sons;


    VId next_vertex=origin;

    list_of_topo_sons=sons(origin,ANY);

    size_t nb=list_of_topo_sons->entries();

    //cout << "**********************************************************" << endl;


    for (size_t i=0;i<nb;i++)
    {
      vertex=list_of_topo_sons->at(i);

      //cout << "Pere : " << origin << " fils : " << vertex;

      if (edgeType(origin,vertex)==LESS)
      {
        //cout << "  Less Son";
        branch->addElement(BranchElement(vertex));
        next_vertex=vertex;
      }
      else
      {
        //cout << " Plus Son";
        vqueue.insert(vertex);
      }
      // cout << endl;
    }


    origin=next_vertex;
    delete list_of_topo_sons;

   }


//  cout << "[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]" << endl;

  _branches->insert(new Branch (*branch));

  delete branch_element;
  delete branch;

  while (!vqueue.isEmpty())
  {
    vertex=vqueue.get();
    lookForBranches(vertex);
  }



}


VIdList* Plant::lookForComponents(VId vertex,IntType level)
{
  VIdList* result;

  if (_mtg->vscale(vertex) != level)
    result=_mtg->compoSons(vertex,level);
  else {
    // _mtg->scale(vertex) == level
    result = _mtg->topoDescendants(vertex, ANYTOPO);
  }
  // note that the result may be an empty array => leading to an invalid PLANTFRAME

  return result;
}

VIdList* Plant::lookForComponents(const VIdList* vid_list,IntType level)
{
  VIdList* result;

  result=new VIdList;

  for (size_t i=0;i<vid_list->entries();i++)
  {
    VId vertex=vid_list->at(i);

    VIdList* tmp_result;
    if (_mtg->vscale(vertex) != level)
      tmp_result=_mtg->compoSons(vertex,level);
    else {
      // _mtg->scale(vertex) == level
      tmp_result = _mtg->topoDescendants(vertex, ANYTOPO);
    }
    // note that the result may be an empty array => leading to an invalid PLANTFRAME

 //   for (size_t j=0;j<tmp_result->entries();j++)
 //   {
 //     result->insert(tmp_result->at(j));
	  if(result->empty())*result = *tmp_result;
	  else result->insert_after(result->previous(result->end()),
						  tmp_result->begin(),tmp_result->end());

  //  }


    delete tmp_result;
  }

  return result;
}

BranchElement Plant::searchForElement(VId vertex) const
{
  IntType nb_branches=_branches->entries();
  AmlBoolean end_of_loop=FALSE;
  BranchElement result;
  IntType i=0;

  while ((!end_of_loop) && (i<nb_branches))
  {
    const BranchCompoList* branche=&_branches->at(i)->branchComponents();
    BranchElement be(vertex);

    if (branche->contains(be))
    {
      end_of_loop=TRUE;
      return branche->at(branche->index(be));
    }
    else
    {
      i++;
    }
  }

  if (!end_of_loop)
  {
    result=BranchElement(UNDEF);
  }

  // assert(end_of_loop);

  return result;
}

VIdList* Plant::sons(VId vertex,EType edge) const
{

  VIdList* result;

  MyNode a_node(vertex,vertex);

  size_t index=_myTree->index(&a_node);

  if (index!=RW_NPOS)
  {

    MyNode* the_node=_myTree->at(index);

    if (edge==LESS)
    {
      result=the_node->getLessSons();
    }
    if (edge==PLUS)
    {
      result=the_node->getPlusSons();
    }
    if (edge==ANY)
    {
      result=the_node->getPlusSons();
      VIdList* list2=the_node->getLessSons();

      size_t nb_elem=list2->entries();

      for(size_t i=0;i<nb_elem;i++)
      {
        result->insert(list2->at(i));
      }

      delete list2;
    }
  }
  else
  {
  result= new VIdList;
  }

  return result;
}

EType Plant::edgeType(VId v1, VId v2) const
{
  EType result=NONE;

  if ((v1!=UNDEF) && (v2!=UNDEF))
  {
    if (topoFather(v2,LESS)==v1)
    {
      result=LESS;
    }
    else
    {
      if (topoFather(v2,PLUS)==v1)
      {
        result=PLUS;
      }
    }
  }

  return result;
}

VId Plant::findLocalTopoRoot(VId vertex, EType edge) const
{
  VId result=_mtg->findLocalTopoRoot(vertex,edge);

  return result;
}


VIdList* Plant::theRoots(VId , IntType)
{
  VIdList* result=new VIdList;

  IntType nb=_components->entries();

  for (IntType i=0;i<nb;i++)
  {
    VId vertex=_components->at(i);

    VId father=topoFather(vertex,ANY);

    if ((father==UNDEF) && (!result->contains(vertex)))
    {
      result->append(vertex);
    }
  }

  return result;
}

void Plant::lookForFather(MyNode& a_node)
{

  VId result=UNDEF;
  VId vertex=a_node.getVertex();
  EType edge=NONE;

  VId father=_mtg->topoFather(vertex,ANY);

  if (_defaultEdge==NONE)
  {
    if (father!=UNDEF)
    {
      edge=_mtg->edgeType(father,vertex);
    }
  }
  else
  {
    if (father!=UNDEF)
    {
      result=father;
      edge=_mtg->edgeType(father,vertex);
    }
    else
    {
      VId precision=_mtg->location(vertex);

      if (precision!=UNDEF)
      {
        IntType scale=_mtg->vscale(precision);
        VId compo_father=_mtg->compoFather(vertex,scale);

        if (compo_father!=UNDEF)
        {
          EType relation=_mtg->edgeType(precision,compo_father);

          if (relation!=NONE)
          {

            VIdList* vertex_brothers=_mtg->compoSons(compo_father,_mtg->vscale(vertex));
            VIdList* precision_brothers=_mtg->compoSons(precision,_mtg->vscale(vertex));

            IntType nb_brothers=vertex_brothers->entries();
            IntType nb_prec_brothers=precision_brothers->entries();

            if (vertex_brothers->at(0)==vertex)
            {
              if (nb_prec_brothers!=0)
              {
                result=precision_brothers->at(nb_prec_brothers-1);
                edge=relation;
              }
            }
            else
            {
              edge=_defaultEdge;
              IntType index=vertex_brothers->index(vertex);
              result=vertex_brothers->at(index-1);
            }

            delete vertex_brothers;
            delete precision_brothers;
          }
        }
      }
      else
      {
        VId compo_father=_mtg->compoFather(vertex);
        VIdList* vertex_brothers=_mtg->compoSons(compo_father,_mtg->vscale(vertex));
        IntType index=vertex_brothers->index(vertex);

        if (index!=0)
        {
          edge=_defaultEdge;
          result=vertex_brothers->at(index-1);
        }

        delete vertex_brothers;
      }
    }
  }

  if (result!=UNDEF)
  {
    if (!_components->contains(result))
    {
      result=UNDEF;
    }
  }


  a_node.putFather(result);
  a_node.putRelation(edge);

  // Update the father's sons.

  if (result!=UNDEF)
  {
    size_t index=_myTree->index(new MyNode (result));

    if (index!=RW_NPOS)
    {
      MyNode* father_node=_myTree->at(index);


      if (edge==PLUS)
      {
        father_node->addPlusSons(a_node.getVertex());
      }
      if (edge==LESS)
      {
        father_node->addLessSons(a_node.getVertex());
      }
    }
  }
}

VId Plant::topoFather(VId vertex,EType edge) const
{


  VId result=UNDEF;

  if ((_defaultEdge!=NONE) || (_isSympodial==TRUE))
  {
    MyNode a_node(vertex);

    size_t index=_myTree->index(&a_node);

    if (index!=RW_NPOS)
    {
      MyNode* the_node=_myTree->at(index);

      if ((the_node->getRelation()==edge) || (edge==ANY))
      {
        result=the_node->getFather();
      }
      // delete the_node;
    }
    else
    {
     // cout << "TopoFather non trouve. " << endl;
    }
  }
  else
  {
    // If there's no reconstitution of the tree, we use mtg's topoFather method.

    result=_mtg->topoFather(vertex,edge);

    if (!_components->contains(result))
    {
      // For sub trees representations: we must verify if the topo father is
      // an component.

      result=UNDEF;
    }
  }
  // cout << "TopoFather : Vertex : " << vertex << " Father : " << result << "  Relation:";
/*
  if (edge==PLUS)
  {
    cout << "   " << "PLUS" << endl;
  }
  if (edge==LESS)
  {
    cout << "   " << "LESS" << endl;
  }
  if (edge==NONE)
  {
    cout << "   " << "NONE" << endl;
  }
  if (edge==ANY)
  {
    cout << "   " << "ANY" << endl;
  } */

 // cout << " == " << result << endl;

  return result;
}


VIdList* Plant::topoSons(VId vertex, EType edge) const
{
  return sons(vertex,edge);
}

IntType Plant::vscale(VId vertex) const
{
  return _mtg->vscale(vertex);
}

IntType Plant::pathLength(VId father, VId vertex, EType edge) const
{
  IntType result=0;

  if (_defaultEdge==NONE)
  {
    result= _mtg->pathLength(father, vertex, edge);
  }
  else
  {

    if (_level!=_mtg->vscale(vertex))
    {
      result=_mtg->pathLength(father,vertex,edge);

      if (result==0)
      {
        vertex=_mtg->compoFather(vertex,_level);
        father=_mtg->compoFather(vertex,_level);
      }
    }

    if ((result==0) && (vertex!=UNDEF) && (father!=UNDEF))
    {
      VId tmp_vertex=vertex;
      result=0;
      AmlBoolean end_of_loop=((tmp_vertex==UNDEF) || (tmp_vertex==father));
      while(!end_of_loop)
      {
        tmp_vertex=topoFather(vertex,edge);

        if ((tmp_vertex==UNDEF) || (tmp_vertex==father))
        {
          end_of_loop=TRUE;
        }
        else
        {
          result++;
        }
      }

      if (tmp_vertex==UNDEF)
      {
        result=0;
      }
    }
  }

  return result;
}

VId Plant::location(VId vertex) const
{
  return _mtg->location(vertex);
}

VIdList* Plant::compoSons(VId vertex) const
{
  return _mtg->compoSons(vertex);
}

VIdList* Plant::compoSons(VId vertex, IntType level) const
{
  return _mtg->compoSons(vertex,level);
}


void Plant::buildMyTree()
{
  // PASS ONE

  size_t nb_elements=_components->entries();

  // cerr << "PASS 1 " << flush;

  for(size_t i=0;i<nb_elements;i++)
  {
    VId vertex=_components->at(i);
    VId father=_mtg->topoFather(vertex,ANY);

    VIdList* list1=_mtg->topoSons(vertex,PLUS);
    VIdList* list2=_mtg->topoSons(vertex,LESS);

    size_t nb1=list1->entries();
    size_t nb2=list2->entries();

    VIdList* plus_sons=new VIdList;
    VIdList* less_sons=new VIdList;

    for(size_t j1=0;j1<nb1;j1++)
    {
      if (_components->contains(list1->at(j1)))
      {
        plus_sons->insert(list1->at(j1));
      }
    }

    for(size_t j=0;j<nb2;j++)
    {
      if (_components->contains(list2->at(j)))
      {
        less_sons->insert(list2->at(j));
      }
    }

    delete list1;
    delete list2;

    // Verify if the father is in the components list.
    // This happens in the case of a sub tree representation.


    if (!_components->contains(father))
    {
      father=UNDEF;
    }


    EType relation=NONE;

    if (father!=UNDEF)
    {
      relation=_mtg->edgeType(father,vertex);
    }


    MyNode* a_node=new MyNode (vertex,father,plus_sons,less_sons);

    a_node->putRelation(relation);

    _myTree->insert(a_node);

    delete less_sons;
    delete plus_sons;
  }

  // PASS TWO
  // cerr << "PASS 2 " << flush;

  nb_elements=_myTree->entries();

  for(size_t i2=0;i2<nb_elements;i2++)
  {
    MyNode* a_node=_myTree->at(i2);

    if (a_node->getFather()==UNDEF)
    {
      lookForFather(*a_node);
    }
  }

  // cerr << "PASS 2 " << endl;;
}

void Plant::buildSympodialTree()
{
  // PASS ONE

  // Il n'y a que la premiere passe qui change.

  size_t nb_elements=_components->entries();

  for(size_t i=0;i<nb_elements;i++)
  {
    VId vertex=_components->at(i);
    VId father=_mtg->topoFather(vertex,ANY);

    VId compo_father=_mtg->compoFather(vertex);

    AmlBoolean is_linear=FALSE;

    if (compo_father!=UNDEF)
    {
      VClass compo_class=_mtg->vclass(compo_father);
      IntType vde=_mtg->classVdecomp(compo_class);

      is_linear=(vde==PLUSLINEAR) || (vde==LESSLINEAR) || (vde==LINEAR) || (vde==PLUSPURELINEAR) || (vde==LESSPURELINEAR) || (vde==PURELINEAR);
    }

    VIdList* list1=_mtg->topoSons(vertex,PLUS);
    VIdList* list2=_mtg->topoSons(vertex,LESS);

    size_t nb1=list1->entries();
    size_t nb2=list2->entries();

    //    cout << "Fils du Vertex " << vertex << endl;

    // cout << "\tAVANT transfo : " << endl;
    /*
    VIdListIter nexta(*list1);
    VIdListIter nextb(*list2);

    cout << "\tListes des fils PLUS : ";
    while (nexta()) { cout << nexta.key() << " ";}
    cout << endl;
    cout << "\tListes des fils LESS : ";
    while (nextb()) { cout << nextb.key() << " ";}
    */


    // Si c'est lineaire les PlusSons deviennent LessSons si ils
    // ont le meme complexe que leur topoFather.

    AmlBoolean is_pure_linear=FALSE;

    VIdListIter next(*list1);

    while (next())
    {
      VId p_son=next.key();

      VId compo_p_son=_mtg->compoFather(p_son);

      if ((compo_p_son==compo_father) && (is_linear))
      {
        next.remove();
        list2->insert(p_son);
      }
      else
      {
        // Recherche du premier ancetre commun et purement lineaire

        IntType ll=_mtg->vscale(vertex)-2;

        while (ll>=0)
        {
          VId vertex_ancestor=_mtg->findCompoAncestorAtScale(vertex,ll);
          VId son_ancestor=_mtg->findCompoAncestorAtScale(p_son,ll);

          if (vertex_ancestor==son_ancestor)
          {

            VClass ancestor_class=_mtg->vclass(vertex_ancestor);
            IntType p_line=_mtg->classVdecomp(ancestor_class);

            is_pure_linear=(p_line==PLUSPURELINEAR) || (p_line==LESSPURELINEAR) || (p_line==PURELINEAR);

            // Pour eviter le Bug, is_pure_linear est toujours a FALSE.
            // D'apres son initialisation plus haut.

            if (is_pure_linear)
            {
              next.remove();
              list2->insert(p_son);
              ll=-1; // Forcer la sortie de la boucle.
            }
          }
          ll--;

        }
      }
    }


    nb1=list1->entries();
    nb2=list2->entries();


    VIdList* plus_sons=new VIdList;
    VIdList* less_sons=new VIdList;


    // cout << "\n\tAPRES transfo : " << endl;

    // cout << "\tListes des fils PLUS : ";

    for(size_t j=0;j<nb1;j++)
    {
      if (_components->contains(list1->at(j)))
      {
        plus_sons->insert(list1->at(j));
        // cout << list1->at(j) << " ";
      }
    }

    // cout << endl;
    // cout << "\tListes des fils LESS : ";

    for(size_t j2=0;j2<nb2;j2++)
    {
      if (_components->contains(list2->at(j2)))
      {
        less_sons->insert(list2->at(j2));
        // cout << list2->at(j) << " ";
      }
    }

    delete list1;
    delete list2;

    // cout << "------------------------------------------" << endl;

    // Verify if the father isn't in the components list.
    // This could happen in the case of a sub tree representation.

    // cout << "Vertex : " << vertex << " :  Father : " << father << endl;

    if (!_components->contains(father))
    {
      father=UNDEF;
    }

    EType relation=NONE;

    if (father!=UNDEF)
    {
      relation=_mtg->edgeType(father,vertex);
      VId compo_father_father=_mtg->compoFather(father);

      if (is_linear && compo_father_father == compo_father) {

        relation=LESS;

      }
      else {

        IntType ll=_mtg->vscale(vertex)-2;

        while (ll>=0)
        {
          VId vertex_ancestor=_mtg->findCompoAncestorAtScale(vertex,ll);
          VId father_ancestor=_mtg->findCompoAncestorAtScale(father,ll);

          if (vertex_ancestor==father_ancestor)
          {
            VClass ancestor_class=_mtg->vclass(vertex_ancestor);
            IntType p_line=_mtg->classVdecomp(ancestor_class);

            is_pure_linear=(p_line==PLUSPURELINEAR) || (p_line==LESSPURELINEAR) || (p_line==PURELINEAR);

            if (is_pure_linear)
            {
              relation=LESS;
              ll=-1; // Forcer la sortie de la boucle.
            }
          }
          ll--;

        }
      }

    }

    /*
    cout << "\n\t==> Create a node :" << endl;
    VIdListIter nextp(*plus_sons);
    VIdListIter nextl(*less_sons);

    cout << "\tFather : " << father ;
    if (relation == PLUS) cout << " -+-> ";
    else if (relation == LESS) cout << " -<-> ";
    else if (relation == NONE) cout << " -X-> ";
    else cout << " -?-> ";
    cout << vertex << endl;

    cout << "\tListes des fils PLUS : ";
    while (nextp()) { cout << nextp.key() << " ";}
    cout << endl;
    cout << "\tListes des fils LESS : ";
    while (nextl()) { cout << nextl.key() << " ";}
    cout << endl;

    */

    MyNode* a_node=new MyNode (vertex,father,plus_sons,less_sons);

    a_node->putRelation(relation);

    _myTree->insert(a_node);

    delete less_sons;
    delete plus_sons;

  }



  // PASS TWO

  nb_elements=_myTree->entries();

  for(size_t i2=0;i2<nb_elements;i2++)
  {
    MyNode* a_node=_myTree->at(i2);

    if (a_node->getFather()==UNDEF)
    {
      lookForFather(*a_node);
    }
  }


}

void Plant::testSons()
{
  IntType nb_comp=_components->entries();

  for(IntType i=0;i<nb_comp;i++)
  {
    VId vertex=_components->at(i);
    VId father=topoFather(vertex,ANY);

    cout << "VERTEX : " << vertex << endl;
    cout << "Father : " << father << endl;

    cout << "RELATION : ";

    if (edgeType(father,vertex)==LESS)
    {
      cout << "   LESS. " << endl;
    }

    if (edgeType(father,vertex)==PLUS)
    {
      cout << "   PLUS. " << endl;
    }

    if (edgeType(father,vertex)==NONE)
    {
      cout << "   NONE. " << endl;
    }

    VIdList* list1=sons(vertex,PLUS);
    VIdList* list2=sons(vertex,LESS);

    IntType nb1=list1->entries();

    cout << "PLUS : ";

    for (IntType j=0;j<nb1;j++)
    {
      cout << list1->at(j) << " " << endl;
    }

    cout << endl;
    IntType nb2=list2->entries();
    cout << "LESS : ";
    for (IntType k=0;k<nb2;k++)
    {
      cout << list2->at(k) << " " << endl;
    }
    cout << endl;
  }

}
void Plant::compare()
{
  IntType nb=_myTree->entries();

  for (IntType i=0;i<nb;i++)
  {
    cout << "COMPARE SONS OF A VERTEX : " << _components->at(i);

    MyNode my_node(_components->at(i));
    IntType index=_myTree->index(&my_node);

    VId vertex=_myTree->at(index)->getVertex();

    cout << " --> (in MyTree) " << vertex << endl;

    cout << "PLUS SONS" << endl;

    if (areEqualLists(sons(vertex,PLUS),_mtg->topoSons(vertex,PLUS)))
    {
      cout << "Bon..." << endl;
    }
    else
    {
      cout << "ERREUR" << endl;
    }

    cout << "LESS SONS" << endl;

    if (areEqualLists(sons(vertex,LESS),_mtg->topoSons(vertex,LESS)))
    {
      cout << "Bon..." << endl;
    }
    else
    {
      cout << "ERREUR" << endl;
    }
    cout << "-------------------------------------------------------------" << endl;
  }
}



AmlBoolean Plant::areEqualLists(VIdList* list1,VIdList* list2)
{
  AmlBoolean result=TRUE;

  if  (list1->entries()!=list2->entries())
  {
    cout << "Inegalite dans la taille. " << endl;
    result=FALSE;
  }
  else
  {
    IntType i=0;
    while ((i<list1->entries()) && (result))
    {
      if (list1->at(i)!=list2->at(i))
      {
        cout << "Inegalite des elements." << endl;
        result=FALSE;
      }
      i++;
    }
  }

  return result;
}



void Plant::report()
{
  IntType nb=_branches->entries();

  cout << "RAPPORT DE LA CLASSE PLANT" << endl << endl << endl;
  cout << "Nombre de branches : " << nb << endl << endl;
  cout << "Composants des branches : " << endl;

  for (IntType i=0;i<nb;i++)
  {

    Branch* branche=_branches->at(i);

    cout << "   Support " << branche->getSupport();
    cout << " Numero de la plante : " << branche->_plantNumber << endl;

  }
}







