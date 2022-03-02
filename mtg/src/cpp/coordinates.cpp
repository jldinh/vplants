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
 *       $Id: coordinates.cpp 17611 2014-10-17 13:20:41Z pradal $
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
#include "sam_msg.h"
#include "math.h"

#include "dressingfile.h"
#include "plant.h"
#include "squares.h"

#define NB_PER_LINE 10


#include "plantframe.h"
#include "coordinates.h"
#include "geomcomputer.h"
#include "forms.h"

#include "tool/rw_queue.h"
#include "tool/rw_list.h"
//#include <rw/tqueue.h>
//#include <rw/tvslist.h>

#include <assert.h>
#include "tool/util_math.h"
#include <iostream>

using namespace std;

Coordinates::Coordinates(Plant* plant,
                         const DressingFile* dressing_file,
                         ValType dist,
                         ValType scale):Measures(plant,NULL,scale)

{
  _areValidCoordinates=TRUE;
  _dressingFile=dressing_file;
  _origin=MyVector (0,0,0);

  if (dist==0)
  {
    dist=_dressingFile->getDefaultDistance();
  }

  _squares=new Squares(dist/_dressingFile->getLengthUnit());
}

Coordinates::~Coordinates()
{
  delete _squares;

}


void  Coordinates::coord3D(VId vertex, ValType* v) const
{
  BranchElement v_element=_plant->searchForElement(vertex);

  if (v_element.getVertex()==UNDEF)
  {
    cout << APPL_MSG[COORD_ERR] << v_element.getVertex() << ". " << endl;
    cout << "This vertex, which was  passed as an argument to AML Coord function,  does not belong to the computed plant frame!!!" <<   endl;
  }
  else
  {
    MyVector elem = v_element.getOrigin() + v_element.getDirp();
    v[0]= elem[0];
    v[1]= elem[1];
    v[2]= elem[2];
  }

}

void  Coordinates::coord3DOrigin(VId vertex, ValType* v) const
{
  BranchElement v_element=_plant->searchForElement(vertex);

  if (v_element.getVertex()==UNDEF)
  {
     cout << APPL_MSG[COORD_ERR] << v_element.getVertex() << ". " << endl;
     cout << "This vertex, which was  passed as an argument to AML Coord function,  does not belong to the computed plant frame!!!" <<   endl;
  }
  else
  {
    MyVector elem = v_element.getOrigin();
    v[0]= elem[0];
    v[1]= elem[1];
    v[2]= elem[2];
  }

}

static void computeEulerAngles(const BranchElement* br,
                               const GeomComputer* geo,
                               MyVector& direction,
                               MyVector& direction_s) {

  // on recupere les valeurs des angles

  Measures* teta_obj = geo->_teta;
  Measures* phi_obj = geo->_phi;
  Measures* psi_obj = geo->_psi;

  ValType teta= teta_obj->lookForFeature(br->getVertex());
  ValType phi= phi_obj->lookForFeature(br->getVertex());
  ValType psi= psi_obj->lookForFeature(br->getVertex());

  /*
  cerr << "Angles d'Euler du vertex : ";
  cerr << br->getVertex() << endl;
  cerr << "\tteta = " << teta << endl;
  cerr << "\tphi  = " << phi << endl;
  cerr << "\tpsi  = " << psi << endl;
  */

  // on calcule les directions primaire, secondaire

  direction = MyVector(MyCos(teta)*MyCos(phi),
                       MySin(teta)*MyCos(phi),
                       -MySin(phi));
  direction_s = MyVector(-MySin(teta)*MyCos(psi)+MyCos(teta)*MySin(phi)*MySin(psi),
                         MyCos(teta)*MyCos(psi)+MySin(teta)*MySin(phi)*MySin(psi),
                         MySin(psi)*MyCos(phi));

  // les vecteurs direction et direction_s sont automatiquement normes.
}


void Coordinates::computeBranchCoordinates(Branch& branch)
{
  IntType category=branch.getCategory();

  // cerr << "         " << " :Passage dans computeBranchCoordinates" << endl;

  Forms* form=_dressingFile->getBranchForm(category);

  if (form)
  {

    // cerr << "form was not NULL" << endl;
    form->modifBranchForm(*branch._components);

    size_t nb_element=branch._components->entries();
    //  ValType delta_alpha=branch._alpha-branch._components->at(0).getAlpha();

    if (branch._alpha!=LUNDEF)
    {
      branch._components->at(0).putAlpha(branch._alpha);
    }

    for(size_t i=0;i<nb_element;i++)
    {
      MyVector limit=computeElementCoordinatesWithForm(branch._components->at(i));

      MyVector max=maxVector(limit,_plant->_maxpoint);
      MyVector min=minVector(limit,_plant->_minpoint);

      _plant->_maxpoint=max;
      _plant->_minpoint=min;
    }
  }
  else
  {
    // cerr << "form was NULL" << endl;

    size_t nb_element=branch._components->entries();

    ValType alpha=branch._alpha;

    if (alpha==LUNDEF)
    {
      alpha=_dressingFile->getDefaultAlpha()/_dressingFile->getAlphaUnit();
    }

    for(size_t i=0;i<nb_element;i++)
    {
      MyVector limit=computeElementCoordinates(branch._components->at(i),alpha);


      MyVector max=maxVector(limit,_plant->_maxpoint);
      MyVector min=minVector(limit,_plant->_minpoint);

      _plant->_maxpoint=max;
      _plant->_minpoint=min;

    }
  }
}

MyVector Coordinates::computeElementCoordinates(BranchElement& br,ValType insert_angle)
{

  VId vertex = br.getVertex();

  VId father=_plant->topoFather(vertex,ANY);
  ValType x,y,z;

  /*
  cerr << "Passage dans computeElementCoordinates ---" << endl;
  cerr << "\tVertex :" << br.getVertex() << endl;
  cerr << "\tPere   :" << father << endl << endl;
  */
  /*
  if (father!=UNDEF) {
    BranchElement father_element=_plant->searchForElement(father);
    MyVector vo = father_element.getOrigin();
    MyVector ve = father_element.getOrigin() + father_element.getDirp();
    vo.report();
    ve.report();
  }
  */

  if (father==UNDEF)
  {
    ValType x0=0; //_origin[0]+_plant->_maxpoint[0]*2;
    ValType y0=0; //_origin[1]+_plant->_maxpoint[1];
    ValType z0=0; //_origin[2]+_plant->_maxpoint[2];

    if (_plant->_root_list) {

      /*
      cerr << endl;
      cerr << "Origin computed for vertex " << vertex << flush;
      */

      int index = _plant->_root_list->index(vertex);

      if (index != RW_NPOS) {

        if (_plant->_origin) { // an array of origins has been defined
          // cerr << " index found: " << index << flush;
          x0 = _plant->_origin[3*index];
          y0 = _plant->_origin[3*index+1];
          z0 = _plant->_origin[3*index+2];
        }

      }

      // cerr << endl;

    }

    MyVector max=maxVector(MyVector(x0,y0,z0),_plant->_maxpoint);
    MyVector min=minVector(MyVector(x0,y0,z0),_plant->_minpoint);

    _plant->_maxpoint=max;
    _plant->_minpoint=min;

    PlantFrame* pf = _plant->_plantframe; // contenu dans un objet "Measures"
    CoordGeom* geo = (CoordGeom*) (pf->_geomComputer);

    MyVector dirp (0,0,1);
    // MyVector dirp (M_PI/2,0);

    /*
    cerr << "Vertex " << vertex << " = dirp (M_PI/2,0) = " << endl;
    dirp.report();
    */

    MyVector dirs (1,0,0);
    // MyVector dirs(0,0);

    // on ecrase ces directions par defaut si on peut utiliser des angles d'Euler
    if (geo->euler(vertex)) {

      computeEulerAngles(&br, geo, dirp, dirs);

    }

    MyVector origin(x0,y0,z0);
    ValType alpha=M_PI/2;
    ValType beta=0;

    ValType length = br.getLength();

    if (length!=0.)
    {
      alpha=dirp.computeAlpha();
      beta=dirp.computeBeta();
    }

    _origin=origin+_origin;

    dirp.multiply(length);

    br.putDirp(dirp);
    br.putDirs(dirs);
    br.putOrigin(origin);
    br.putAlpha(alpha);
    br.putBeta(beta);

    x=dirp[0]+origin[0];
    y=dirp[1]+origin[1];
    z=dirp[2]+origin[2];

  }
  else
  {
    ValType beta=br.getBeta();
    ValType alpha=0;
    ValType ratio=1;

    BranchElement father_element=_plant->searchForElement(father);

    MyVector v;

    if (_plant->edgeType(father,vertex)==PLUS)
    {
      alpha=insert_angle;
      ratio=computeRatio(father,vertex);
      // cerr << "\tvertex " << vertex << " : ratio = " << ratio << endl;
      beta=br.getBeta();

      if (_dressingFile->isAlphaRelative())
      {
        v=putOn(father_element,br, alpha, beta, ratio );
      }
      else
      {
        v=putOnAbs(father_element,br, alpha, beta, ratio );
      }

    }
    else
    {
      v=putOn(father_element,br,alpha,beta,ratio);
    }

    x=v[0];y=v[1];z=v[2];

  }

  MyVector result(x,y,z);

  return result;
}

IntType Coordinates::computeCategory(VId vertex)
{
  // En principe ici on fait appel a un objet qui contient les methodes
  // pour le calcul de la categorie.

  VId father=_plant->topoFather(vertex,ANY);
  IntType result=UNDEF;

  if (father==UNDEF)
  {
    result=1;
  }

 return result;
}

MyVector Coordinates::computeElementCoordinatesWithForm(BranchElement& br)
{

  VId father=_plant->topoFather(br.getVertex(),ANY);
  MyVector result;

  if (father==UNDEF)
  {

    ValType x0=0; // _origin[0]+_plant->_maxpoint[0]*2;
    ValType y0=0; //_origin[1]+_plant->_maxpoint[1];
    ValType z0=0; //_origin[2]+_plant->_maxpoint[2];

    MyVector max=maxVector(MyVector(x0,y0,z0),_plant->_maxpoint);
    MyVector min=minVector(MyVector(x0,y0,z0),_plant->_minpoint);

    _plant->_maxpoint=max;
    _plant->_minpoint=min;

    MyVector dirp (M_PI/2,0);
    MyVector dirs (1,0,0);
    MyVector origin(x0,y0,z0);
    ValType alpha=M_PI/2;
    ValType beta=0;

    _origin=origin+_origin;

    dirp.multiply(br.getLength());

    br.putDirp(dirp);
    br.putDirs(dirs);
    br.putOrigin(origin);
    br.putAlpha(alpha);
    br.putBeta(beta);

    ValType x=dirp[0]+origin[0];
    ValType y=dirp[1]+origin[1];
    ValType z=dirp[2]+origin[2];

    result=MyVector (x,y,z);
  }
  else
  {

    ValType alpha=br.getAlpha();
    ValType beta=br.getBeta();
    ValType ratio=1;

    BranchElement father_element=_plant->searchForElement(father);

    if (_plant->edgeType(father,br.getVertex())==PLUS)
    {
      ratio=computeRatio(father,br.getVertex());
    }

    result=putOnAbs(father_element,br, alpha, beta, ratio );

  }

  return result;
}


ValType Coordinates::computeRatio( VId father,VId vertex)
{
  ValType result=VAL_ERROR;

  VId detail=_plant->location(vertex);

  if (_plant->vscale(vertex)>_plant->vscale(detail))
  {
    result=lookForRatio(father,vertex);
  }
  else
  {
    VIdList* list=_plant->compoSons(father,_plant->vscale(detail));

    if (!list->isEmpty())
    {
      VId topo_root=_plant->findLocalTopoRoot(detail,ANY);
      ValType r1=(ValType)_plant->pathLength(topo_root,detail,ANY);
      if (r1==0)
      {
        r1=1;
      }
      ValType r2=(ValType)list->entries();
      result=r2/r1;
    }
    else
    {
      result=1;
    }

    delete list;
  }

  assert(result!=VAL_ERROR);

  return result;
}

ValType Coordinates::lookForRatio(VId father,VId vertex)
{
  ValType result=VAL_ERROR;
  ValType dec_ratio=0.1;

  VIdList* list=_plant->topoSons(father,PLUS);
  IntType nb=list->entries();

  if (nb!=0)
  {
    result=1+(nb+1)*dec_ratio;
  }
  else
  {
    result=1;
  }

  for (IntType i=0;i<nb;i++)
  {
    if (vertex!=list->at(i))
    {
      result-=dec_ratio;
    }
  }

  delete list;

  assert(result!=VAL_ERROR);

  return result;
}


MyVector Coordinates::maxVector( MyVector v1,MyVector v2 )
{
  ValType x=MAX(v1[0],v2[0]);
  ValType y=MAX(v1[1],v2[1]);
  ValType z=MAX(v1[2],v2[2]);

  MyVector result(x,y,z);

  return result;
}

MyVector Coordinates::minVector( MyVector v1,MyVector v2 )
{
  ValType x=MIN(v1[0],v2[0]);
  ValType y=MIN(v1[1],v2[1]);
  ValType z=MIN(v1[2],v2[2]);

  MyVector result(x,y,z);

  return result;
}

// When the primary direction is determined by digitizing the enpoints of a segment
// or equivalently by giving two angles alpha (insertion) and beta (azimut), the
// secundary direction of the element is underspecified, unless a "roulis" angle
// is given. In this case, it can be used to compute the secondary direction.
// The following function returns such a secundary direction.

static MyVector findSecondaryDirection(ValType b, // second euler angle
                                       ValType a, // first euler angle
                                       ValType c  // third euler angle
  ) {

  return MyVector(-MySin(a)*MyCos(c) + MyCos(a)*MySin(b)*MySin(c),
                  MyCos(a)*MyCos(c) + MySin(a)*MySin(b)*MySin(c),
                  MyCos(b)*MySin(c));
}


/* Coordinates::putOn is used if alpha is a relative angle (default) */

MyVector Coordinates::putOn(const BranchElement& base,
                            BranchElement& element,
                            const ValType alpha0,
                            const ValType beta,
                            const ValType ratio)
{

  assert(element.getLength()!=VAL_ERROR);

  assert(base.isValid());

  ValType alp=base.getAlpha();
  ValType bet=base.getBeta();
  ValType length_of_support=base.getLength();
  MyVector  origin_of_support=base.getOrigin();

  ValType alpha=M_PI/2-alpha0;

  // cerr << "Vertex " << element.getVertex() << " :Passage dans PutOn" << endl;

  MyVector w=base.getDirp();
  MyVector v=base.getDirs();
  MyVector u=base.getDirt();

  w.norm();
  u.norm();
  v.norm();

  /*
  cerr << "Repere : " << endl;
  u.report();
  v.report();
  w.report();

  cerr << "u^v : " << (u^v) << "  v^w " << (v^w) << " u^w " << (u^w) << endl;
  */

  // (o,u,v,w) constitue le repere par rapport auquel les coordonnees
  // ont ete calculees.

  // Calcul des coordonnees du vecteur par rapport au repere (u,v,w)
  // les angles alpha et beta sont supposes relatifs (i.e. donnes dans
  // ce repere

  MyVector direction;
  MyVector direction_s;

  PlantFrame* pf = _plant->_plantframe; // contenu dans un objet "Measures"
  CoordGeom* geo = (CoordGeom*) (pf->_geomComputer);

  ValType length;

  // Calcul avec les angles d'euler
  if (geo->euler(element.getVertex())) {

    computeEulerAngles(&element, geo, direction, direction_s);

    // ESSAI: le texte suivant est inserre
    Measures* len = geo->_length;
    ValType result= len->lookForFeature(element.getVertex());

    if (result!= LUNDEF) length = result;
    else {
	  length = ((CoordLength *)len)->getMinLength(element.getVertex());
	}
    // FIN ESSAI

  }
  else { // sinon on utilise alpha et beta (insertion et azimut / porteur)

    direction = MyVector(alpha,beta);

    // ON ramene les coordonnees au repere orthonorme global

    direction.changeRepere(u,v,w); // on passe dans le repere global

    // Fin des modifications sur le calcul de l'origine.

    direction.norm();

    // Calcul de la direction secondaire.
    // Cette direction est arbitraire sauf si l'angle de roulis est donne
    // par l'utilisateur:

    ValType roulis= 0; // si le roulis n'est pas donne, il est nul

    if (geo->_psi) {
      roulis= geo->_psi->lookForFeature(element.getVertex());
      if (roulis == LUNDEF) roulis = 0;
      // else cerr << "roulis(" << element.getVertex() << ") = " << roulis << endl;
    }
    direction_s = findSecondaryDirection(alpha, beta, roulis);
    // direction_s.multiply(-1.0);

    // cerr << "Ds av rep :";
    // direction_s.report();

      // cerr << "Dp^Ds : " << (tmp_dirp^direction_s) << endl;


    direction_s.changeRepere(u,v,w);

    /*
      cerr << "Ds ap rep :";
      direction_s.report();
      cerr << endl;
    */

    direction_s.norm();

    length = element.getLength();

  }

  MyVector basedirp=base.getDirp();

  //basedirp.norm();


  // heuristique: quand rien est connu, la position du porte
  // est a une fraction de la longueur du porteur dependant du
  // nombre de composants du porteur (cf. computeRatio)

  // basedirp.multiply(length_of_support/ratio);
  // basedirp.multiply(length_of_support);

  MyVector new_origin=basedirp+origin_of_support;

  /*
  cerr << "Les produit scalaire des directions :(put ON) " << endl;
  direction.report();
  direction_s.report();

  direction.norm();

  cerr << "Produit scalaire P^S : " << (direction^direction_s) << endl;

  cerr << "-----------------------------------" << endl;
  */


  // Update the fields

  // cerr << "Vertex " << element.getVertex() << " length = " << length << endl;

  direction.multiply(length);

  element.putDirp(direction);
  element.putDirs(direction_s);

  element.putOrigin(new_origin);
  ValType al=0,be=0;

  if (direction.computeLength()!=0)
  {
    al=direction.computeAlpha();
    be=direction.computeBeta();
  }

  element.putAlpha(al);
  element.putBeta(be);

  MyVector result(direction);

  result=result+element.getOrigin();

  return result;
}


/* Coordinates::putOnAbs is used if alpha is an absolute angle */

MyVector Coordinates::putOnAbs(const BranchElement& base,
                               BranchElement& element,
                               const ValType alpha,
                               const ValType beta,
                               const ValType ratio)
{
  assert(element.getLength()!=VAL_ERROR);

  assert(base.isValid());

  MyVector direction;
  MyVector direction_s;

  PlantFrame* pf = _plant->_plantframe;
  CoordGeom* geo = (CoordGeom*) (pf->_geomComputer);

  if (geo->euler(element.getVertex())) {

    computeEulerAngles(&element, geo, direction, direction_s);

  }
  else {

    direction = MyVector(alpha,beta);

    direction.norm();

    ValType dsx=-MySin(beta);
    ValType dsy=MyCos(beta);

    direction_s = MyVector(dsx,dsy,0);

    direction_s.norm();

  }

  ValType alp=base.getAlpha();
  ValType bet=base.getBeta();
  ValType length_of_support=base.getLength();
  MyVector  origin_of_support=base.getOrigin();

  MyVector new_origin(alp,bet);


  // new_origin.multiply(length_of_support/ratio);
  new_origin.multiply(length_of_support);

  new_origin=new_origin+origin_of_support;

  MyVector direction_t=direction*direction_s;
  direction_t.norm();

  direction.multiply(element.getLength());

  // Update the fields

  element.putDirp(direction);
  element.putDirs(direction_s);
  element.putOrigin(new_origin);
  element.putAlpha(alpha);
  element.putBeta(beta);

  MyVector result(direction);

  result=result+element.getOrigin();

  /*
  cerr << "Les trois directions (put on ABS) : " << endl;

  direction.report();
  direction_s.report();
  direction_t.report();

  direction.norm();

  cerr << "Produit scalaire P^S : " << (direction^direction_s) << endl;
  cerr << "Produit scalaire P^T : " << (direction^direction_t) << endl;
  cerr << "Produit scalaire S^T : " << (direction_s^direction_t) << endl;

  cerr << "-----------------------------------" << endl;
  */

  return result;

}


void Coordinates::newTrunk(size_t index)
{

  if (_squares->getNbVoxels()!=0)
  {
    size_t last=_squares->getNbVoxels()-1;
    _squares->_voxels->at(last).putMax(_plant->_maxpoint);
    _squares->_voxels->at(last).putMin(_plant->_minpoint);
  }

  _plant->_maxpoint=MyVector(-MAX_VALTYPE,-MAX_VALTYPE,-MAX_VALTYPE);
  _plant->_minpoint=MyVector(MAX_VALTYPE,MAX_VALTYPE,MAX_VALTYPE);

  _squares->addVoxel(Voxel(index));

}

void Coordinates::lastTrunk()
{
  size_t last=_squares->getNbVoxels()-1;
  _squares->_voxels->at(last).putMax(_plant->_maxpoint);
  _squares->_voxels->at(last).putMin(_plant->_minpoint);

}

void Coordinates::translateBranch(Branch* br, ValType dx, ValType dy, ValType dz )
{
  MyVector delta(dx,dy,dz);

  for(size_t i=0;i<br->_components->entries(); i++)
  {
    MyVector new_origin=br->_components->at(i).getOrigin()+delta;
    br->_components->at(i).putOrigin(new_origin);
  }
}



void Coordinates::translatePlantElements()
{

  _squares->computePositions((size_t)_dressingFile->getNbPlantsPerLine());

  MyVector max=_plant->_maxpoint;
  MyVector min=_plant->_minpoint;

  MyVector*& t = _plant->_translation;

  for(size_t i=0;i<_plant->_branches->entries();i++)
  {
    ValType dx,dy,dz;

    if (t) {

      dx = (*t)[0];
      dy = (*t)[1];
      dz = (*t)[2];

    }
    else {

      if (_plant->_branches->at(i)->getSupport()==UNDEF)
      {
        Voxel v(i);
        size_t index=_squares->_voxels->index(v);

        dx=_squares->_voxels->at(index).getDeltaX();
        dy=_squares->_voxels->at(index).getDeltaY();
        dz=_squares->_voxels->at(index).getDeltaZ();

        max=maxVector(_squares->_voxels->at(index).getMax(),max);
        min=minVector(_squares->_voxels->at(index).getMin(),min);
      }

    }

    translateBranch(_plant->_branches->at(i),dx,dy,dz);

  }

    if (t) {
      _plant->_minpoint=min + (*t);
      _plant->_maxpoint=max + (*t);
    }
    else {
      _plant->_minpoint=min;
      _plant->_maxpoint=max;
    }

}




void Coordinates::translatePlantElements(MyVector delta)
{

  for(size_t i=0;i<_plant->_branches->entries();i++)
  {

    translateBranch(_plant->_branches->at(i),delta[0],delta[1],delta[2]);

  }

  // _plant->_minpoint=min;
  // _plant->_maxpoint=max;

}





// Classe requiredcoords


typedef RWTQueue<BranchElement,RWTValDlist<BranchElement> > BrQueue;

RequiredCoords::RequiredCoords(Plant* plant,
                               FNode* xxf,
                               FNode* yyf,
                               FNode* zzf,
                               CoordsType coord_type,
                               const DressingFile* dressingfile,
                               ValType dist,
                               ValType scale=1):Coordinates(plant, dressingfile,dist,scale)
{
  // Look for the reference system

  _isValidRefSystem=FALSE;
  _sysLevel=UNDEF;
  _level=UNDEF;

  _xcoord=0;
  _ycoord=0;
  _zcoord=0;

  if (coord_type==TRIANGULAR)
  {
    if (lookForRefSystem())
    {

      _xcoord=new L1Coord (plant,xxf,scale);
      _ycoord=new L2Coord (plant,yyf,scale);
      _zcoord=new L3Coord (plant,zzf,scale);

      if (_xcoord->getLevel()!=UNDEF)
      {
        _level=_xcoord->getLevel()+1; // The first inquired coordinates are the origines.
        _isValidRefSystem=TRUE;
      }
    }
  }
  else
  {
    _refSystem=new CartesianRefSystem ();
    _xcoord=new XCoord (plant,xxf,scale);
    _ycoord=new YCoord (plant,yyf,scale);
    _zcoord=new ZCoord (plant,zzf,scale);

    if (_xcoord->getLevel()!=UNDEF)
    {
      _level=_xcoord->getLevel()+1; // The first inquired coordinates are the origines.
      _isValidRefSystem=TRUE;
    }
  }

  _areValidCoordinates=_isValidRefSystem;
}

RequiredCoords::~RequiredCoords()
{
  if (_isValidRefSystem)
  {
    delete _xcoord;
    delete _ycoord;
    delete _zcoord;
    delete _refSystem;
  }
}



AmlBoolean RequiredCoords::lookForRefSystem()
{
  AmlBoolean result=FALSE;
  IntType dab_index=UNDEF;
  IntType dbc_index=UNDEF;
  IntType dac_index=UNDEF;

  for(IntType i=0;i<_plant->featureNb();i++)
  {
    if (_plant->fname(i)==TR_DAB)
    {
      dab_index=i;
    }

    if (_plant->fname(i)==TR_DAC)
    {
      dac_index=i;
    }

    if (_plant->fname(i)==TR_DBC)
    {
      dbc_index=i;
    }
  }

  if ((dab_index!=UNDEF) &&
      (dac_index!=UNDEF) &&
      (dbc_index!=UNDEF))
  {
    VId root=_plant->mtgRoot();
    VId vertex=_plant->_vertex;

    ValType dab=0,dbc=0,dac=0;


    while ((vertex!=UNDEF) && (!(findFeature(vertex,dab_index,dab) &&
                                 findFeature(vertex,dbc_index,dbc) &&
                                 findFeature(vertex,dac_index,dac))))
    {
      vertex=_plant->compoFather(vertex);

    }

    if (vertex==UNDEF)
    {
      cout << APPL_MSG[REFERENCE_MSG] << endl;
      _isValidRefSystem=FALSE;
    }
    else
    {
      _refSystem=new TriangRefSystem (dab,dac,dbc);
      _isValidRefSystem=TRUE;
      _sysLevel=_plant->vscale(vertex);
    }

    result=_isValidRefSystem;
  }

  return result;
}

// Cherche les coordonnees d'origine d'un element de branche
// Celles ci ont soit deja ete calculees (inferrees) par induction
// soient doivent etre disponibles sur le porteur. Seules les coordonnees
// d'origine de la racine sont renseignees dans son complexe passe en 1er argument
// dans l'appelle a PlantFrame
// sinon (0,0,0) est renvoye.

MyVector RequiredCoords::lookForOrigin(BranchElement& branch_element)
{
  // Recherche l'origine d'un element de la branche
  // Cette methode doit calculer les coordonnees de n'importe quel
  // element de la plante recursivement.

  MyVector result(0,0,0);

  VId vertex = branch_element.getVertex();

  // cerr << "vertex dont on cherche l'origine : " << vertex << endl;
  VId support=_plant->location(vertex);
  // VId support=_plant->topoFather(vertex,ANY);
  // cerr << "son support est  : " << support << endl;

  if (support == -1) {

    ValType* porigin = _plant->_origin;

    if (porigin) { // cas ou l'origine a ete specifiee par une option

      return MyVector(porigin[0],porigin[1],porigin[2]);

    }
    else { // sinon

      // L'origine de la racine est indiquee dans le premier complexe englobant
      // le vertex passe en argument

      int vscale_root = _plant->vscale(_plant->mtgRoot());
      VId support = _plant->compoFather(vertex);

      ValType l1=0,l2=0,l3=0;

    // cerr << "origine de la racine est indiquee au niveau du vertex qui est passe en arg : " << support << endl;

      while ((_plant->vscale(support) > vscale_root) &&
             (!(findFeature(support,_xcoord->_index,l1) &&
                findFeature(support,_ycoord->_index,l2) &&
                findFeature(support,_zcoord->_index,l3))))
      {
        // cerr  << "\t --> coordonnees non trouvees sur vertex " << support << "=> calcul du complex ..." << endl;
        support=_plant->compoFather(support);
      }

      if (_plant->vscale(support) > vscale_root) {

        // cerr  << "\t --> coordonnees trouvees  " << support << " = " << l1 << ", " << l2 << ", " << l3 << endl;

        if (!_refSystem->findPoint(l1,l2,l3,result)) cout << "Error: Wrong coordinates at vertex " << support << endl;

        // cerr << "Voila" << endl;

      }
      else {

        // On a pas trouve les coordonnees d'origine dans le
        // support, a aucune echelle.

        cout << "WARNING : No coordinates found for the origin of this branching system (vertex " << vertex << ")" << endl;
        cout << "WARNING : (0,0,0) is taken as a default origin" << endl;

      }

    }

  }
  else { // Nous ne sommes pas sur la racine du systeme ramifie

    // cerr << "Recherche des coordonnees d'origine de vertex " << vertex << endl;

    // support = _plant->location(support);

    // if (support == UNDEF) cerr << "WARNING the location of vertex " << support << " should not be UNDEF" << endl;

    BranchElement br_s=_plant->searchForElement(support);

    if (br_s.getVertex()!=UNDEF)
    {
      // cerr << "\t --> coordonnees d'origine trouvees sur le vertex " << br_s.getVertex() << endl;
      /*
      br_s.getOrigin().report();
      br_s.getDirp().report();
      */
      result=br_s.getDirp()+br_s.getOrigin();

    }
    else {

      // le support ne fait pas partie des elements a tracer:
      // il peut etre dune echelle plus fine par exemple ou ne pas appartenir
      // a la partie de la plante dont on a demande la visualisation.
      // son origine et sa direction n'ont pas ete inferres
      // on va donc chercher si le support contient une information
      // sur les coordonnees de son extremite a une echelle
      // quelconque.

      ValType l1=0,l2=0,l3=0;
      int vscale_root = _plant->vscale(_plant->mtgRoot());

      while ((_plant->vscale(support)>vscale_root) &&
             (!(findFeature(support,_xcoord->_index,l1) &&
                findFeature(support,_ycoord->_index,l2) &&
                findFeature(support,_zcoord->_index,l3))))
      {
        // cerr  << "\t --> coordonnees non trouvees sur vertex " << support << "=> calcul du complex ..." << endl;
        support=_plant->compoFather(support);
      }

      if (_plant->vscale(support)> vscale_root)
      {
        //cerr  << "\t --> coordonnees trouvees  " << support << " = " << l1 << ", " << l2 << ", " << l3 << endl;
        if (!_refSystem->findPoint(l1,l2,l3,result)) cout << "Error: Wrong coordinates at vertex " << support << endl;
        // cerr << "Voila" << endl;
      }
      else
      { // On a pas trouve les coordonnees d'origine dans le
        // support, a aucune echelle.

        cout << "WARNING : No coordinates found for the origin of this branching system (vertex " << vertex << ")" << endl;
        cout << "WARNING : (0,0,0) is taken as a default origin" << endl;

      }

    }

  }

  return result;
}

/* Ancienne procedure faite par Samir, pour trouver l'origine d'un
element qui n'est pas dans le trace graphique demande par l'utilisateur
(il n'est pas dans l'objet _plant).
Elle ne marche pas, et il faudrait la reprendre entierement. En outre
une telle procedure ne peut pas fournir un resultat identique a celui
que l'on obtiendrait si la plante entiere etait tracee, et ou le trace
des elements serait gere par des algorithmes encore differents */

/*

MyVector RequiredCoords::findOrigin(VId vertex)
{

}

*/


AmlBoolean RequiredCoords::lookForCoords(VId vertex,MyVector& _vect)
{
  AmlBoolean result=FALSE;

  //cerr << "_scale(" << vertex << ")="<<_plant->vscale(vertex);
  //cerr << "_level(" << vertex << ")="<<_level << endl;

  // the following line has been added because the _level is not computed accurately
  // therefore I fix the level to the scale of the vertex whose geometry is to be computed.
  // (normally, the level is computed automatically as the first scale (topdown)
  // whose vertices have attributes.
  _level = _plant->vscale(vertex);

  if (_level!=UNDEF)
  {
    if (_plant->vscale(vertex)>=_level)
    {
      result=lookUpCoords(vertex,_vect);
      /*
      cerr << "Vertex " << vertex << " coord -> " << result << endl;
      _vect.report();
      */
    }
    else { // les coordonnees sont renseignees a un niveau plus microscopique

      // A FAIRE ...

    }

  }

  return result;
}


AmlBoolean RequiredCoords::lookUpCoords(VId vertex, MyVector& _vect)
{

  ValType xx=_xcoord->lookForFeature(vertex);
  ValType yy=_ycoord->lookForFeature(vertex);
  ValType zz=_zcoord->lookForFeature(vertex);

  AmlBoolean result=FALSE;

  if ((xx!=LUNDEF) &&
      (yy!=LUNDEF) &&
      (zz!=LUNDEF))
  {

    // cerr << "vertex :" << vertex << " => xx, yy, zz = " << xx << "," << yy << "," << zz << endl;

    result=_refSystem->findPoint(xx,yy,zz,_vect);
    if (!result) cout << "Error: Wrong coordinates at vertex " << vertex << endl;

    // cerr << "--> " << flush;
    // _vect.report();
  }

  return result;
}

/*
static bool computeAPerpendicularDirection(const MyVector& dir1, MyVector& dir2) {

  // en ecrivant le produit scalaire entre direction et direction_s
  // et en faisant l'hypothese que la direction secondaire est toujours
  // dans le plan y , z (x=0) on obtient les valeurs y et z de la direction
  // secondaire suivantes:

  ValType a=dir1[0], b=dir1[1],c=dir1[2]; // primary direction
  double a2=a*a,b2=b*b,c2=c*c;
  double n2 = a2+b2+c2;
  double eps = 1E-7;

  // cerr << "n2 = " << n2 << endl;

  if (n2 > 3*eps) {
    if (b2+c2>eps) {
      dir2 = MyVector(0.0,c,-b);
    }
    else if (c2+a2>eps) {
      dir2 = MyVector(c,0.0,-a);
    }
    else if (a2+b2>eps) {
      dir2 = MyVector(b,-a,0.0);
    }
    else assert(false);
    return true;
  }
  else {
    return false;
  }
}
*/


static bool computeAPerpendicularDirection(const MyVector& dir1, MyVector& dir2) {

  // the spherical coordinates of dir1 define two Euler angles:

  ValType azimuth = dir1.computeBeta();

  ValType elevation = -dir1.computeAlpha(); // in Euler angles positive angles are oriented downwards

  // cerr << "beta = " << azimuth << endl;

  // The last Euler angle is underdetermined : we fix it
  // at a value such that the secundary direction is correctly
  // oriented with respect to its definition in the Geom library:
  // should be oriented towards the positive x axis when the
  // principal direction is oriented towards the positive z axis.
  // This comes to defining the roling angle as 3*Pi/2:

  double roling = 3.0*M_PI/2.0;

  double sa=MySin(azimuth);
  double sb=MySin(elevation);
  double sc=MySin(roling);
  double ca=MyCos(azimuth);
  double cb=MyCos(elevation);
  double cc=MyCos(roling);

  double a = (-sa*cc)+(ca*sb*sc);
  double b = (ca*cc)+(sa*sb*sc);
  double c = cb*sc;

  dir2 = MyVector(a,b,c);

  // Note: si azimuth=0, elevation = -Pi/2, roling = 3PI/2
  // then dir2 = (1,0,0) which is the requested secundary direction
  // in lib Geom.

  return true;

}



void RequiredCoords::computeBranchCoordinates(Branch& branch)
{

  BrQueue fifo;
  MyVector origin=lookForOrigin(branch._components->at(0));

  /*
  cerr << "Calcul des COORDONNEES des entites de la branche " << endl;

  cerr << "ORIGINE DE LA BRANCHE : base du vertex "<< branch._components->at(0).getVertex() << flush;
  origin.report();
  cerr << "========================" << endl;
  */

  MyVector max=maxVector(origin,_plant->_maxpoint);
  MyVector min=minVector(origin,_plant->_minpoint);

  _plant->_maxpoint=max;
  _plant->_minpoint=min;

  AmlBoolean new_element=TRUE;
  size_t nb_element=branch._components->entries();
  MyVector dirp,dirs;


  PlantFrame* pf = _plant->_plantframe;
  CoordGeom* geo = (CoordGeom*) (pf->_geomComputer);

  for(size_t i=0;i<nb_element;i++)
  {
    BranchElement* branch_element=&branch._components->at(i);
    MyVector vector; // coordinates of the current element

    // cerr << "CALCUL des COORDONNEES du vertex " << branch_element->getVertex() << endl;
    // cerr << "-------------------------------- " << endl;


    if (lookForCoords(branch_element->getVertex(),vector))
    {
       // cerr << "Vertex " << branch_element->getVertex()<< " has coords" << endl;
      new_element=FALSE;

      MyVector max=maxVector(vector,_plant->maxPoint());
      MyVector min=minVector(vector,_plant->minPoint());

      _plant->_maxpoint=max;
      _plant->_minpoint=min;


      MyVector direction;
      MyVector direction_s;
      ValType length;

      // La plupart du temps, la direction primaire d'une entite est determinee
      // par son point d'origine (sommet du pere) et par son extremite.

      // Cependant, dans certains cas (cas d'une feuille dont on mesure
      // l'orientation directement avec un outil de digitalisation (parametre
      // optionel EulerAngle a true pour cette entite) il faut utiliser les angles
      // d'euler pour determiner l'orientation de l'entite dans l'espace
      // (i.e. sa direction primaire et sa direction secondaire).  La longueur
      // de l'entite est cependant toujours determinee par le point sommet ou
      // par la donnee explicite de cette longueur (parametre optionnel Length)

      // Doit-on utiliser les angles d'eulers mesures
      if (geo->euler(branch_element->getVertex())) {

        // on ecrase l'ancienne direction primaire qui a servi a calculer la longueur
        computeEulerAngles(branch_element, geo, direction, direction_s);

        length = (vector-origin).computeLength();

      }
      else {

        // La seconde facon de calculer des coordonnees

        direction=vector-origin;

        length = direction.computeLength();

        ValType eps = 1E-7;
        if (length <= eps) { // this point is equal to the previous one.
          VId father=_plant->topoFather(branch_element->getVertex(),ANY);
          BranchElement father_element=_plant->searchForElement(father);
          direction = father_element.getDirp();
          direction_s = father_element.getDirs();
        }
        else {

          direction.norm();

          // cerr << "*** Direction du vecteur a tracer : " << flush;
          // direction.report();

          if (geo->_psi) {

            ValType roulis= geo->_psi->lookForFeature(branch_element->getVertex());
            if (roulis == LUNDEF) roulis = 0;

            // ValType alpha = direction.computeAlpha();
            // ValType beta = direction.computeBeta();

            // else cerr << "roulis(" << branch_element->getVertex() << ") = " << roulis << endl;
            // cerr << "ROULIS = " << roulis << endl;
            // A VERIFIER !!!!
            // direction_s = findSecondaryDirection(alpha, beta, roulis);
            // direction_s=MyVector(-sin(alpha),cos(alpha),0.0);

            bool b = computeAPerpendicularDirection(direction, direction_s);
            /*
            cerr << "*********************************" << endl;
            direction.report();
            direction_s.report();
            */
            assert(b); // should not be false since direction norm is non 0;
          }
          else {

            bool b = computeAPerpendicularDirection(direction, direction_s);
            assert(b); // should not be false since direction norm is non 0;
            // cerr << "PAS de ROULIS = " << endl;
          }

          direction_s.norm();

        }
      }
      /*
      {
        MyVector prim = direction;
        prim.norm();
        ValType scal = (prim^direction_s);
        if (scal > 0.1) {
          cerr << "Vertex " << branch_element->getVertex() << ": Produit scalaire de direction*direction_s = " << scal << endl;
          cerr << "\tdir prim= "<< flush;
          direction.report();
          cerr << "\tdir sec = "<< flush;
          direction_s.report();
        }
      }
      */

      dirs=direction_s;
      dirp=direction;

      ValType alpha=0;
      ValType beta=0;

      if (length!=0)
      {
        alpha=direction.computeAlpha();
        beta=direction.computeBeta();
      }

      // Traitement des elements qui n'ont pas de coordonnees renseignees.

      // cerr << "Traitement des entites non renseignees : " << endl;

      int flag = 0;

      // on a empile en parcourant la suite des vertex de la branche toute une
      // suite de vertex qui n'ont pas de coordonnees. Mais comme nous sommes
      // la, c'est que nous avons trouve un nouveau vertex qui lui a des
      // coordonnees. On peut donc faire une interpolation lineaire Dans
      // l'attribut Length d'un vertex n'ayant pas de coordonnees, a ete
      // enregistre par la methode computeLength du geomComputer (appelee avant
      // la methode computeCoord qui nous a envoyes ici) une valeur
      // correspondant au pourcentage de la longueur entre les deux vertex ayant
      // des coordonnees definies qu'il faudra utiliser pour le tracer de cette
      // entite.

      // Avant de rentrer dans cette boucle, length contient la longueur total
      // entre les deux points renseignes. Il va donc falloir multiplier cette
      // length par la longueur contenue dans chaque segment non renseigne.

      while(!fifo.isEmpty())
      {
        flag = 1; // il y a au moins un element sans coordonnees entre les deux
                  // points mesures.

        BranchElement br_s=fifo.get();
        IntType index=branch._components->index(br_s);

        // cerr << "Vertex " << br_s.getVertex() << " :vertex SANS COORDONNEES  entre deux ayant des coordonnees"  << endl;

        assert(index!=RW_NPOS);

        BranchElement* br=&branch._components->at(index); // Est-ce utile ???

        ValType br_length=length/br->getLength();


        /*
        cerr << "seg tot length   = " << length << endl;
        cerr << "br->getLength()  = " << br->getLength() << endl;
        cerr << "longeur obtenue  = " << br_length << endl;
        */

        if (geo->euler(br->getVertex())) {

          computeEulerAngles(br, geo, dirp, direction_s);

        }
        else {
          dirp=direction;
        }

        dirp.multiply(br_length);

        br->putDirp(dirp);
        br->putDirs(direction_s);
        br->putOrigin(origin);
        br->putLength(br_length);
        br->putAlpha(alpha);
        br->putBeta(beta);

        origin=origin+dirp;

      }

      // Il ne faut appliquer la regle de division du segment renseigne que si
      // les deux vertex dont les coordonnees sont renseignees sont separes
      // par au moins 1 vertex non renseigne (flag ==1)

      ValType br_length;
      if (flag == 1) br_length = length/branch_element->getLength();
      else br_length = length;

      /*
      cerr << "Length = " << length<< " , br_length = " <<br_length << endl;
      cerr << "Origin = " << flush;
      origin.report();
      */

      direction.multiply(br_length);

      branch_element->putDirp(direction);
      branch_element->putDirs(direction_s);
      branch_element->putAlpha(alpha);
      branch_element->putBeta(beta);
      branch_element->putLength(br_length);
      branch_element->putOrigin(origin);

      origin=direction+origin;

      max=maxVector(vector,_plant->maxPoint());
      min=minVector(vector,_plant->minPoint());

      _plant->_maxpoint=max;
      _plant->_minpoint=min;

    }
    else // element sans coordonnees
    {
      // cerr << "element " << branch_element->getVertex() << " inserted in FIFO" << endl;
      fifo.insert(*branch_element);
    }

  } // Fin de la boucle sur les elements de la branche

  // Il faut maintenant traiter tous les elements qui se retrouvent en fin de
  // branche et qui n'ont pas de coordonnees (on a pas trouve de nouveau vertex
  // ayant des coordonnees avant la fin de la branche. Il faut donc vider la
  // pile existante.

  if (!fifo.isEmpty())
  {
    // Traitement des elements qui n'ont pas de coordonnees.

    // cerr << "          :vertex SANS COORDONNEES en fin de branche"  << endl;

    if (new_element)
    {

      // Il s'agit d'une branche dont aucun element ne dispose de coordonnees.
      // Dans ce cas on fait appel a la methode computeBranchCoordinates de
      // Coordinates (qui tient compte des angles d'euler si necessaire)

      // cerr << "           :dans cette branche aucun vertex n'a de coordonnees"  << endl;
      Coordinates::computeBranchCoordinates(branch);

      fifo.clear();

    }
    else
    {
      // Ces elements devront etre dans le prolongement de la branche.

      // cerr << "           :dans cette branche certain elements omt des coordonnees et il faut tracer les autres dans le prolongement du dernier avec coord"  << endl;

      while(!fifo.isEmpty())
      {
        BranchElement branch_element=fifo.get();
        size_t index=branch._components->index(branch_element);

        assert(index!=RW_NPOS);

        BranchElement* br=&branch._components->at(index);

        // cerr << "On regarde alors le vertex "  << br->getVertex() << endl;

        ValType length;

        // On regarde d'abord s'il y a une valeur par defaut (ceci est donne par
        // la methode lookForFeature de l'objet _length (type Measures*) contenu
        // dans le CoordGeom du plantframe:

        Measures* len = geo->_length;
        ValType result= len->lookForFeature(br->getVertex());

        if (result!= LUNDEF) length = result;
        else length = ((CoordLength*)len)->getMinLength(br->getVertex());

        /*
        cerr << "\nvertex = " << br->getVertex() << endl;
        cerr << "index = " << index << endl;
        cerr << "length = " << length << endl;
        cerr << "result = " << result << endl;
        */

        br->putLength(length);

        // Si on doit tenir compte des angles d'euler pour definir les
        // directions p et s

        if (geo->euler(br->getVertex())) {

          computeEulerAngles(br, geo, dirp, dirs);

        }
        else { // Sinon, on continue dans la meme direction que le pere topologique

          VId father=_plant->topoFather(br->getVertex(),ANY);

          BranchElement father_element=_plant->searchForElement(father);

          dirp = father_element.getDirp();

          dirp.norm();

        }

        ValType alpha=0;
        ValType beta=0;

        if (length!=0)
        {
          alpha=dirp.computeAlpha();
          beta=dirp.computeBeta();
        }

        dirp.multiply(length);

        br->putLength(length);
        br->putDirp(dirp);
        br->putDirs(dirs);
        br->putOrigin(origin);
        br->putAlpha(alpha);
        br->putBeta(beta);

        origin=origin+dirp;

        MyVector max=maxVector(origin,_plant->maxPoint());
        MyVector min=minVector(origin,_plant->minPoint());

        _plant->_maxpoint=max;
        _plant->_minpoint=min;

      }
    }
  }


  assert(fifo.isEmpty());

}




AmlBoolean RequiredCoords::findFeature(VId vertex,
                                    IntType index,
                                    ValType& value)
{
  AmlBoolean result=FALSE;

  const Feature* feature;
  Date date;

  assert(index!=-1);

  // verification du fait que l'attribut est calculable via 1 FNode Du fait que
  // nous sommes dans la classe RequiredCoord, il n'y a seulement besoin de
  // verifier cela pour les attributs Measures* _xcoord, _ycoord, _zcoord

  if (_xcoord) if (_xcoord->_index == index) {
    value = _xcoord->lookForFeature(vertex);
    if (value==LUNDEF) return FALSE;
    else return TRUE;
  }
  if (_ycoord) if (_ycoord->_index == index) {
    value = _ycoord->lookForFeature(vertex);
    if (value==LUNDEF) return FALSE;
    else return TRUE;
  }
  if (_zcoord) if (_zcoord->_index == index) {
    value = _zcoord->lookForFeature(vertex);
    if (value==LUNDEF) return FALSE;
    else return TRUE;
  }

  // pour verification d'autres type d'attributs, le cas echeant:
  // mais il y a un probleme car pour ces attributs on ne verifie
  // pas tout d'abord si ils sont calculables via 1 FNode !!!!
  // A revoir des que possible ...

  if (_plant->hasFeatures(vertex))
  {
    date=_plant->lastDate(vertex);
    feature=_plant->feature(vertex,index,date);

    // cerr << "\tindex = " << index << endl;

    if ( _plant->fType(index) == REAL) {

      int i=feature->i;

      IntType ii=(IntType) i;

      if (ii!=LUNDEF) {

          RVal r;
          r=feature->r;

          // cerr << "\tvalue = " << r << endl;

          if (r!=LUNDEF) {

              value=(ValType)r;
              result=TRUE;

          }
        }

    }
    else { // ASCOMP: For ascendant compatibility will be removed in the future

      IVal i;
      i=feature->i;

      if (i!=LUNDEF)
      {
        value=(ValType)i;
        result=TRUE;

      }

    }

  }
  else {

    // cerr << "vertex " << vertex << " has no features" << endl;
  }

  return result;
}









