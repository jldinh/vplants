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
 *       $Id: virtualelements.cpp 17611 2014-10-17 13:20:41Z pradal $
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




#include <typeinfo>
#include "plantgl/math/util_math.h"
#include "plantgl/math/util_matrix.h"
TOOLS_USING_NAMESPACE

#include "aml/ammodel.h"
#include "aml/array.h"

#include "plantframe.h"
#include "plant.h"
#include "dressingfile.h"
#include "linetree.h"

//#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"

#define  ERR_MSG_ARRAY          mtg_err_msgs_aml
#define  MODULE_NAME            "MTG"
extern const char *mtg_err_msgs_aml[];

using namespace std;

VirtualSymbol::VirtualSymbol()
{
}

VirtualSymbol::VirtualSymbol(IntType number)
{
  _element=number;
}

VirtualSymbol::VirtualSymbol(IntType number, IntType bearing_element)
{
  _element=number;
  _bearing_element=bearing_element;
}


VirtualSymbol::VirtualSymbol(IntType number, IntType bearing_element, IntType color_number, char symb)
{
  _element=number;
  _bearing_element=bearing_element;
  _colorNumber=color_number;
  _symbol=symb;
}

VirtualSymbol::VirtualSymbol(const VirtualSymbol& v)
{
  _element=v._element;
  _bearing_element=v._bearing_element;
  _colorNumber=v._colorNumber;
  _symbol=v._symbol;
}


const VirtualSymbol& VirtualSymbol::operator=(const VirtualSymbol& v)
{

  if (this != &v)
  {
    _element=v._element;
    _bearing_element=v._bearing_element;
    _colorNumber=v._colorNumber;
    _symbol=v._symbol;
  }

  return *this;
}

AmlBoolean VirtualSymbol::operator==(const VirtualSymbol& v ) const
{
  if (_element==v._element)
  {
    return TRUE;
  }
  else
  {
    return FALSE;
  }
}


VirtualElements::VirtualElements(FNode* symbol_fun,
				 FNode* verticille,
				 FNode* elements_number,
				 FNode* virtual_color,
				 FNode* top_dia,
				 FNode* bottom_dia,
				 FNode* length,
				 FNode* alpha,
				 FNode* beta)
				
{

  _symbolFun=symbol_fun;
  _verticille=verticille;
  _color=virtual_color;
  _elementNumber=elements_number;
  //_plant=plant;
  //_dressingFile=dressing_file;
  //_symbolTable=s_t;
  //_dresser=dresser;

  _topDia=top_dia;
  _bottomDia=bottom_dia;
  _length=length;
  _alpha=alpha;
  _beta=beta;
 
}

VirtualElements::~VirtualElements()
{
}


void VirtualElements::setEnvironement(LineTree* lt,
                                      const DressingFile* dressing_file,
                                      Plant* plant)
{
  _plant=plant;
  // _symbolTable=v_symbol_table;
  //_dresser=dresser;
  _dressingFile=dressing_file;

  lt->_isEnvironementSet=TRUE;

  if (_plant!=NULL)
  {
    MTG* mtg = _plant->getMtg();

    _maxVertex= mtg->vertexNb();

    if (lt->_vertexNumber==0)
    {
      lt->_vertexNumber=_maxVertex;
    }

  }

  addVirtualElements(lt);
}

// La fonction addVirtualElements() rajoute des elements virtuels a un plantframe
// deja existant. Ceci est effectue en rajoutant une seule branche a la fin de la
// liste de branches de _plant qui contiendra tous les virtual elements.
// Tout d'abord, on verifie que tous les objets necessaires ont bien ete calcules
// (_isEnvironementSet)


void VirtualElements::addVirtualElements(LineTree* lt)
{
  // Rajoute les elements virtuels a la plante
  
  if (lt->_isEnvironementSet)
  {

    if (_elementNumber!=NULL)
    {

      size_t nb_branches = _plant->nbBranches();
      IntType plant_number = _plant->getPlantCounter()+1;

      Branch* new_branch = new Branch( UNDEF, plant_number);
      lt->_addedBranch=new_branch;

      for (size_t i=0; i<nb_branches; i++)
      {
		const Branch& br = _plant->findBranch(i);
		const BranchCompoList& brcplist = br.branchComponents();
		
		ValType beta=getDefaultBeta();
		ValType base_verticille=beta;
		
		for(size_t j=0; j<brcplist.entries(); j++)
		{
		  VId vertex = brcplist.at(j).getVertex();
		  
		  if (vertex<_maxVertex)
		  {
			
			// Recuperation du nombre d'elements a rajouter.
			
			ValType alpha=getAlpha(vertex);
			ValType be=getBeta(vertex);
			
			if (be!=LUNDEF)
			{
			  beta=be;
			  base_verticille=beta;
			}
			
			IntType nb_elements=(IntType)fnodeValue(_elementNumber,vertex);
			IntType verticille;
			
			if (_verticille!=NULL)
			{
			  verticille=(IntType)fnodeValue(_verticille,vertex);
			}
			else
			{
			  verticille=_dressingFile->getDefaultVerticille();
			}
			
			//cout << "Generate elements with beta=" << beta << endl;
			
			generateElements(lt, nb_elements, 
			  verticille, 
			  vertex, 
			  alpha, 
			  beta,
			  new_branch, 
			  base_verticille);
			
		  }
		}
     }
	  _plant->_branches->insert(new_branch);
    }
  }
}

void VirtualElements::generateElements(LineTree* lt, 
									   IntType nb_elements,
									   IntType verticille, 
									   VId vertex, 
									   ValType alpha, 
									   ValType& beta, 
									   Branch* branch,
									   ValType base_verticille)
{

  // Genere les elements virtuels et les insert dans la branche.

  ValType start_angle=beta;

  BranchElement base=_plant->searchForElement(vertex);
  ValType rotate_beta=start_angle;
  ValType base_beta=(2*M_PI/(ValType) verticille); // Angle entre deux elements.

  //cout << "Verticille : " << base_beta << endl;

  // Longueur du  support.

  //cout << "Vertex : " << vertex << "  Beta : " << beta*180/M_PI << endl;


  ValType support_lentgh=base.getLength();
  IntType nb_floors=(IntType)ceil((ValType) nb_elements/(ValType) verticille);

  IntType floor_number=1;

  ValType ratio=(ValType)nb_floors/(ValType)floor_number;

  for( IntType n=1; n<=nb_elements; n++)
  {

    // a new virtual vertex is created with identifier _vertexNumber
    // which equals _maxvertex + the number of currently inserted
    // element (_vertexNumber is incremented at the end of this loop)
    BranchElement br(lt->_vertexNumber);

    char a_symb=getDefaultSymbol();
	
    if (_symbolFun!=NULL)
    {
      a_symb=(char)fnodeValue(_symbolFun, vertex);
    }

    IntType color_number=19;
	
    if (_color!=NULL)
    {
      color_number=(IntType)fnodeValue(_color, vertex);
    }

    //lt->insertVirtualSymbol(_vertexNumber,color_number,a_symb);
	
    // vertex is the actual vertex bearing the virtualelement whose
    // number is _vertexNumber.
    // cerr << "virtual element " << lt->_vertexNumber << " added." << endl;
	
    lt->_virtualTable->insert(VirtualSymbol (lt->_vertexNumber,vertex, color_number,a_symb) );
	
    computeElementLength(br,vertex);
    computeElementTopDia(br,vertex);
    computeElementBottomDia(br,vertex);
    br.putAlpha(alpha);
    br.putBeta(rotate_beta);
	
    // cout << "Put on element : Alpha " << alpha << "   Rotate Beta : " << rotate_beta << endl;
	
    MyVector limit=putOnElement( base, br, alpha, rotate_beta, ratio);
	
    MyVector max=maxVector(limit,_plant->_maxpoint);
    MyVector min=minVector(limit,_plant->_minpoint);
    _plant->_maxpoint=max;
    _plant->_minpoint=min;
	
    branch->_components->insert(br);

    if ((n % verticille) == 0 )
    {
      floor_number++;     
      ratio=(ValType)nb_floors/(ValType)floor_number;
	  
      start_angle+=base_verticille;
	  
      if (start_angle > (M_PI*2))
      {
		start_angle=start_angle-(M_PI*2);
      }
	  
      //cout << "Beta prochain element (element mm verticille) : " << (start_angle)*180/M_PI << endl;
	  
      rotate_beta=start_angle;
    }
    else
    {
      rotate_beta+=base_beta;
    }
    if (rotate_beta>=(M_PI*2))
    {
      rotate_beta=rotate_beta-(M_PI*2);
    } 
	
    lt->_vertexNumber++;
  }
  
  //cout << "Beta en sortie : " << (start_angle)*180/M_PI << endl;
  
  beta=start_angle;
  
  //cout << "---------------------------------------------" << endl;
}


ValType VirtualElements::fnodeValue(FNode* function,VId vertex)
{
/*  if(function){
	cerr << "Apply fnode : \"" << function->name() << '"';
	cerr << "with " << function->argNb() << " arg."  <<endl;
  }
  else cerr << "Apply NULL fnode." << endl;*/
  assert(function);

  ValType result=VAL_ERROR;

  AMObjVector argobjs(1); // Only one arg which is a vertex

  argobjs[0] = AMObj(AMObjType::VTX, vertex);

  AMObj result_obj = function->apply(argobjs);

  switch(result_obj.tag()) {

  case  AMObjType::INTEGER:
    result = (double) result_obj.val.i;
    break;
  case  AMObjType::REAL:
    result = result_obj.val.r;
    break;
 case  AMObjType::CHAR:
    result = (double) result_obj.val.c;
    break;

  default:
    //cerr << "Erreur !!" << endl;
    //cerr << "vtx  = " << vertex << endl;
    //cerr << "f(.) = " << result_obj << endl;
    result = (ValType) LUNDEF;
  }

  assert(result!=VAL_ERROR);

  return result;
}

// Fonction qui calcule les coordonnees, les diametres et orientation
// de tout virtual element. Elle est appelee par
// VirtualElements::generateElements()

MyVector  VirtualElements::putOnElement(const BranchElement& base,
					BranchElement& element,
					ValType alpha0, 
					ValType beta, 
					ValType ratio)
{

  assert(element.getLength()!=VAL_ERROR);

  assert(base.isValid());

  ValType alp=base.getAlpha();
  ValType bet=base.getBeta();
  ValType length_of_support=base.getLength();
  MyVector  origin_of_support=base.getOrigin();

  ValType alpha=M_PI/2-alpha0;

  element.putAlpha(alpha);
  element.putBeta(beta);

  MyVector new_origin=computeElementOrigin(base,element,ratio);

  // On regarde s'il y a une translation a faire
  MyVector*& t = _plant->_translation;
  if (t) new_origin = new_origin +(*t);

  MyVector direction=computePrimerDirection(base,element);

  direction.norm();

  element.putDirp(direction);

  MyVector direction_s=computeSecondDirection(base,element);

  MyVector direction_t=computeThirdDirection(direction,direction_s,base); 

  // Update the fields

  direction.multiply(element.getLength());

  element.putDirp(direction);
  element.putDirs(direction_s);
  element.putOrigin(new_origin);

  /*
  cerr << "Feuille : " << endl;
  direction.report();
  direction_s.report();
  direction_t.report();
  */

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

  direction.norm();
/*
  cout << "Produit scalaire P^S : " << (direction^direction_s) << endl;
  cout << "Produit scalaire P^T : " << (direction^direction_t) << endl;
  cout << "Produit scalaire S^T : " << (direction_s^direction_t) << endl;

  cout << "-----------------------------------" << endl;*/

  return result;
}

MyVector VirtualElements::computeElementOrigin(const BranchElement& base ,
                                               BranchElement& element, ValType ratio)
{
  // Calcul l'origine d'un fruit/fleur ou  feuille.

  MyVector direction=base.getDirp();
  MyVector origin_of_support=base.getOrigin();
  ValType length_of_support=base.getLength();

/*
  cerr << "**** Nouvelle origine :" << endl;
  cerr << "direction = " << endl;
  direction.report();
  cerr << "origin = " << endl;
  origin_of_support.report();
  cerr << "length = " << length_of_support << endl;
*/
  direction.norm();

  direction.multiply(length_of_support/ratio);

  // On rajoute le rayon

  ValType l1=length_of_support;
  ValType l=l1 - (l1/ratio);
  ValType d1=base.getBotDia();
  ValType d2=base.getTopDia();

/*
  cerr << "ratio = " << ratio << endl;
  cerr << "d1 = " << d1 << endl;
  cerr << "d2 = " << d2 << endl;
  cerr << " l = l1 - (l1/ratio) = " << d2 << endl;
*/
  ValType d=(l1/l)*(d1-d2)+d2;

  if (l==0)
  {
    d=d2;
  }

  // cerr << "if (l==0) then d=d2 else d = (l1/l)*(d1-d2)+d2" << d << endl;

  ValType beta=element.getBeta();

  MyVector w=base.getDirp();
  MyVector u=base.getDirs();
  MyVector v=base.getDirt();

  w.norm();
  u.norm();
  v.norm();

  MyVector trans(0,beta);

  trans.changeRepere(u,v,w);

  trans.norm();
  trans.multiply(d/2);

  direction=direction+trans; // La somme des deux vecteurs donne l'origine exacte

  // On remet l'origine

  direction=direction+origin_of_support;

  return direction;
}


// La base est l'element porteur de la feuille ou du fruit. Cette base definit un repere
// local Rloc definit comme suit.
// Axe des z = direction principale de l'element = w
// Axe des x = direction secondaire de l'element = u
// Axe des y = direction tertiare.               = v
//
// Soit la matrice P des vecteurs colonnes de la base Rloc exprimes dans la base Rglob
// P = (u, v, w)
// Soit un vecteur V exprime dans Rloc, note V/Rloc, on a les coordonnees de V/Rglob
// par la formule de changement de repere :
// V/Rglob = P V/Rloc

#define TOOLS_DIRECTION


MyVector VirtualElements::computePrimerDirection(const BranchElement& base, BranchElement& element)
{

  ValType alpha=element.getAlpha();//M_PI/2-element.getAlpha();
  ValType beta=element.getBeta();

  MyVector w=base.getDirp();
  MyVector u=base.getDirs();
  MyVector v=base.getDirt();

  w.norm();
  u.norm();
  v.norm();

#ifdef TOOLS_DIRECTION
  Vector3 _direction = Matrix3::eulerRotationZYX(Vector3(beta,-alpha,0)).getColumn(0);
  MyVector direction(_direction.x(),_direction.y(),_direction.z());
#else
  MyVector direction(alpha,beta); // direction exprimee dans Rloc
#endif
  // cout << " Direction principale : (alpha,beta)=(" << alpha*180/M_PI << "," << beta*180/M_PI << ")" << endl;

  direction.changeRepere(u,v,w);  // exprime direction dans Rglob

  direction.norm();

  return direction;
}


MyVector VirtualElements::computeSecondDirection(const BranchElement& base, BranchElement& element)
{

  ValType alpha=element.getAlpha();//M_PI/2-element.getAlpha();
  ValType beta=element.getBeta();
  
  MyVector w=base.getDirp();
  MyVector u=base.getDirs();
  MyVector v=base.getDirt();

  w.norm();
  u.norm();
  v.norm();
  
#ifdef TOOLS_DIRECTION
  Vector3 _direction = Matrix3::eulerRotationZYX(Vector3(beta,-alpha,0)).getColumn(1);
  MyVector direction_s(_direction.x(),_direction.y(),_direction.z());
#else
  MyVector direction_s (0,beta+M_PI/2);
#endif
  // cout << " Direction secondaire : (alpha,beta)=(" << 0 << "," << (beta+M_PI/2)*180/M_PI << ")" << endl;

  direction_s.changeRepere(u,v,w);

  direction_s.norm();

  return direction_s;
}

MyVector VirtualElements::computeThirdDirection(MyVector& v1, MyVector& v2,const BranchElement&)
{
  MyVector result=v1*v2;

  return result;
}

void VirtualElements::computeElementLength(BranchElement& br, VId father)
{
  ValType result;

  if (_length!=NULL)
  {
    result=fnodeValue(_length,father)/_dressingFile->getLengthUnit();
    // cerr << "length " << father << " = " << result << endl;
  }
  else
  {
    result=getDefaultLength();
  }

  br.putLength(result);

}

void VirtualElements::computeElementTopDia(BranchElement& br,VId father)
{

  ValType result=LUNDEF;

  if (_topDia!=NULL)
  {
    result=fnodeValue(_topDia,father)/_dressingFile->getDiametersUnit();
  }

  if (result==LUNDEF)
  {
    result=getDefaultTopDia();
  }

  br.putTopDia(result);

}



void VirtualElements::computeElementBottomDia(BranchElement& br,VId father)
{
  ValType result=LUNDEF;

  if (_bottomDia!=NULL)
  {
    result=fnodeValue(_bottomDia,father)/_dressingFile->getDiametersUnit();
  }

  if(result==LUNDEF)
  {
    result=getDefaultBottomDia();
  }

  br.putBotDia(result);

}


ValType VirtualElements::getAlpha(VId father)
{
  ValType result=LUNDEF;

  if (_alpha!=NULL)
  {
    result=fnodeValue(_alpha,father)/_dressingFile->getAlphaUnit();
  }

  if (result==LUNDEF)
  {
    result=getDefaultAlpha();
  }

  return result;
}

ValType VirtualElements::getBeta(VId father)
{
  ValType result=LUNDEF;

  if (_beta!=NULL)
  {
    result=fnodeValue(_beta,father)/_dressingFile->getAzimutUnit();
  }
  /*
  if (result==LUNDEF)
  {
    result=getDefaultBeta();
  }*/

  return result;
}



MyVector VirtualElements::maxVector( MyVector v1,MyVector v2 )
{
  ValType x=MAX(v1[0],v2[0]);
  ValType y=MAX(v1[1],v2[1]);
  ValType z=MAX(v1[2],v2[2]);

  MyVector result(x,y,z);

  return result;
}

MyVector VirtualElements::minVector( MyVector v1,MyVector v2 )
{
  ValType x=MIN(v1[0],v2[0]);
  ValType y=MIN(v1[1],v2[1]);
  ValType z=MIN(v1[2],v2[2]);

  MyVector result(x,y,z);

  return result;
}


ostream& VirtualElements::displayOneLine(ostream& o) const
{
  o << "Virtual Element. " << endl;

  return o;
}

// Classe de feuilles virtuelles

VirtualLeaves:: VirtualLeaves(FNode* symbol_fun,
			      FNode* verticille,
			      FNode* elements_number,
			      FNode* color,
			      FNode* top_dia,
			      FNode* bottom_dia,
			      FNode* length,
			      FNode* alpha,
			      FNode* beta)
: VirtualElements( symbol_fun, verticille, elements_number,
		  color, top_dia, bottom_dia, length, alpha, beta )
{
}

VirtualLeaves::~VirtualLeaves()
{
}

ostream& VirtualLeaves::displayOneLine(ostream& o) const
{
  o << "Virtual leaves. " << endl;

  return o;
}

// Pour les feuilles, en general la direction primaire dans la ligne elastique
// correspond a la direction du petiole. La direction secondaire correspond
// a une droite perpendiculaire dans le plan de la feuille. La direction
// tertiare correspond a la normale orientee positivement en sortant de la face
// photosynthetique de la feuille.

MyVector VirtualLeaves::computeSecondDirection(const BranchElement& base, BranchElement& element)
{

  ValType alpha=element.getDirp().computeAlpha();
  ValType beta=element.getDirp().computeBeta();

  MyVector w=base.getDirp(); // direction of the bearing component
  w.norm();

  // Here the secundary direction is defined by w * p which will
  // make the limb of the ternary direction of the leaf in the same
  // direction as the bearing axis, which is usually what is expected
  MyVector dirp = element.getDirp();
  MyVector direction_s = w * dirp;

#ifdef TOOLS_DIRECTION
  // Add gamma rotation (Roll)
/*  if(gamma != 0){
	Vector3 _direction(direction_s[0],direction_s[1],direction_s[2]);
	Vector3 axis(dirp[0],dirp[1],dirp[2]);
	//_direction = Matrix3::axisRotation(axis,gamma)*_direction;
	direction_s = MyVector(_direction.x(),_direction.y(),_direction.z());
  }*/
#endif

  direction_s.norm();

  return direction_s;

}

MyVector VirtualLeaves::computeThirdDirection(MyVector& v1, MyVector& v2,const BranchElement& base)
{

  MyVector result=v1*v2;

  VId vertex=base.getVertex();

  BranchElement el;

  computeElementTopDia(el,vertex);

  ValType fact=el.getBotDia();

  result.multiply(fact);

  return result;
}

char VirtualLeaves::getDefaultSymbol()
{
  return _dressingFile->getLeafSymbol();
}


ValType VirtualLeaves::getDefaultAlpha()
{
  return _dressingFile->getDefaultLeafAlpha()/_dressingFile->getAlphaUnit();
}

ValType VirtualLeaves::getDefaultBeta()
{
  return _dressingFile->getDefaultLeafBeta()/_dressingFile->getAzimutUnit();
}

ValType VirtualLeaves::getDefaultLength()
{
  return _dressingFile->getDefaultLeafLength()/_dressingFile->getLengthUnit();
}

ValType VirtualLeaves::getDefaultTopDia()
{
  return _dressingFile->getDefaultLeafTopDia()/_dressingFile->getDiametersUnit();
}

ValType VirtualLeaves::getDefaultBottomDia()
{
  return _dressingFile->getDefaultLeafBottomDia()/_dressingFile->getDiametersUnit();
}

// ---------------------
// Feuilles DIGITALISEES
// ---------------------

VirtualDigitizedLeaves::VirtualDigitizedLeaves(FNode* symbol_fun,
					       FNode* verticille,
					       FNode* elements_number,
					       FNode* color,
					       FNode* top_dia,
					       FNode* bottom_dia,
					       FNode* length,
					       FNode* alpha,
					       FNode* beta,
					       FNode* xx,	  
					       FNode* yy,	  
					       FNode* zz,	  
					       FNode* teta,	  
					       FNode* phi,	  
					       FNode* psi)
: VirtualElements(symbol_fun, verticille, elements_number,
		  color, top_dia, bottom_dia, length, alpha, beta)
{
  _xx = xx;
  _yy = yy;
  _zz = zz;
  _teta = teta;
  _phi = phi;
  _psi = psi;
}

VirtualDigitizedLeaves::~VirtualDigitizedLeaves()
{
}

MyVector VirtualDigitizedLeaves::computeCoords(const BranchElement& base, BranchElement& br) {

  ValType xx,yy,zz;

  VId vertex = base.getVertex();

  if (_xx!=NULL) // FNode pour xx
  {
    xx=fnodeValue(_xx,vertex);
  }
  else
  {
    xx=0;
  }

  if (_yy!=NULL) // FNode pour yy
  {
    yy=fnodeValue(_yy,vertex);
  }
  else
  {
    yy=0;
  }

  if (_zz!=NULL) // FNode pour zz
  {
    zz=fnodeValue(_zz,vertex);
  }
  else
  {
    zz=0;
  }

  MyVector result(xx,yy,zz);

  /*
  cout << "*** Coordonnees  =";
  result.report();
  */
  // la direction primaire est utilisee temporairement pour stocker les
  // coordonnees

  br.putDirp(result);

  return result;

}

MyVector VirtualDigitizedLeaves::computeEulerAngles(const BranchElement& base, BranchElement& br) {

  ValType teta,phi,psi;

  VId vertex = base.getVertex();

  if (_teta!=NULL) // FNode pour teta
  {
    teta=fnodeValue(_teta,vertex);
  }
  else
  {
    teta=0;
  }

  if (_phi!=NULL) // FNode pour phi
  {
    phi=fnodeValue(_phi,vertex);
  }
  else
  {
    phi=0;
  }

  if (_psi!=NULL) // FNode pour psi
  {
    psi=fnodeValue(_psi,vertex);
  }
  else
  {
    psi=0;
  }

  MyVector result(teta,phi,psi);

  /*
  cout << "*** Angles d'Euler = ";
  result.report();
  */

  br.putDirs(result);

  return result;

}


MyVector VirtualDigitizedLeaves::computeElementOrigin(const BranchElement& base,
                                                      BranchElement& element,
                                                      ValType ratio)
{

  // la direction primaire est utilisee pour stocker les coordonnees
  // calculees par computeCoord

  computeCoords(base, element);

  MyVector coord = element.getDirp();
  return coord;
}


// Angles d'euler
MyVector VirtualDigitizedLeaves::computePrimerDirection(const BranchElement& base,
                                                        BranchElement& element)
{

  // la direction secondaire est utilisee pour stocker les angles

  computeEulerAngles(base, element);

  MyVector angles = element.getDirs(); // retrieve the computed Euler angles

  ValType teta = angles[0];
  ValType phi = angles[1];

  return MyVector(MyCos(teta)*MyCos(phi),
                  MySin(teta)*MyCos(phi),
                  -MySin(phi));
}

MyVector VirtualDigitizedLeaves::computeSecondDirection(const BranchElement& base, BranchElement& element)
{

  // la direction secondaire est utilisee pour stocker les angles

  MyVector angles = element.getDirs();

  ValType teta = angles[0];
  ValType phi = angles[1];
  ValType psi = angles[2];

  /*
  cout << "Angles d'Euler du vertex : ";
  cout << base.getVertex() << endl;
  cout << "\tteta = " << teta << endl;
  cout << "\tphi  = " << phi << endl;
  cout << "\tpsi  = " << psi << endl;
  */

  return MyVector(-MySin(teta)*MyCos(psi)+MyCos(teta)*MySin(phi)*MySin(psi),
                  MyCos(teta)*MyCos(psi)+MySin(teta)*MySin(phi)*MySin(psi),
                  MySin(psi)*MyCos(phi));

}

MyVector VirtualDigitizedLeaves::computeThirdDirection(MyVector& v1, MyVector& v2,const BranchElement& base)
{

  return MyVector(v1*v2);

}

char VirtualDigitizedLeaves::getDefaultSymbol()
{
  return _dressingFile->getLeafSymbol();
}


ValType VirtualDigitizedLeaves::getDefaultAlpha()
{
  return _dressingFile->getDefaultLeafAlpha()/_dressingFile->getAlphaUnit();
}

ValType VirtualDigitizedLeaves::getDefaultBeta()
{
  return _dressingFile->getDefaultLeafBeta()/_dressingFile->getAzimutUnit();
}

ValType VirtualDigitizedLeaves::getDefaultLength()
{
  return _dressingFile->getDefaultLeafLength()/_dressingFile->getLengthUnit();
}

ValType VirtualDigitizedLeaves::getDefaultTopDia()
{
  return _dressingFile->getDefaultLeafTopDia()/_dressingFile->getDiametersUnit();
}

ValType VirtualDigitizedLeaves::getDefaultBottomDia()
{
  return _dressingFile->getDefaultLeafBottomDia()/_dressingFile->getDiametersUnit();
}

ostream& VirtualDigitizedLeaves::displayOneLine(ostream& o) const
{
  o << "Virtual digitized leaves. " << endl;

  return o;
}



// Classe pour les fruits virtuels

VirtualFruits:: VirtualFruits(FNode* symbol_fun,
			      FNode* verticille,
			      FNode* elements_number,
			      FNode* color,
			      FNode* top_dia,
			      FNode* bottom_dia,
			      FNode* length,
			      FNode* alpha,
			      FNode* beta)
: VirtualElements( symbol_fun, verticille, elements_number,
		  color, top_dia, bottom_dia, length, alpha, beta)
{
}

VirtualFruits::~VirtualFruits()
{
}

ostream& VirtualFruits::displayOneLine(ostream& o) const
{
  o << "Virtual fruits. " << endl;

  return o;
}

MyVector VirtualFruits::computeSecondDirection(const BranchElement& base, BranchElement& element)
{
  //MyVector tmp=VirtualElements::computeSecondDirection(base,element);

  ValType alpha=element.getAlpha();
  ValType beta=element.getBeta();

  MyVector direction_s (0,beta+M_PI/2);

  direction_s.norm();

  VId vertex=base.getVertex();

  return direction_s;

}


MyVector VirtualFruits::computePrimerDirection(const BranchElement& base, BranchElement&)
{

  MyVector direction(-M_PI/2,0);

  direction.norm();

  return direction;
}

ValType VirtualFruits::getDefaultAlpha()
{
  return _dressingFile->getDefaultFruitAlpha()/_dressingFile->getAlphaUnit();
}

char VirtualFruits::getDefaultSymbol()
{
  return _dressingFile->getFruitSymbol();
}

ValType VirtualFruits::getDefaultBeta()
{
  return _dressingFile->getDefaultFruitBeta()/_dressingFile->getAzimutUnit();
}

ValType VirtualFruits::getDefaultLength()
{
  return _dressingFile->getDefaultFruitLength()/_dressingFile->getLengthUnit();
}

ValType VirtualFruits::getDefaultTopDia()
{
  return _dressingFile->getDefaultFruitTopDia()/_dressingFile->getDiametersUnit();
}

ValType VirtualFruits::getDefaultBottomDia()
{
  return _dressingFile->getDefaultFruitBottomDia()/_dressingFile->getDiametersUnit();
}

// Classe pour les fleurs virtuels

VirtualFlowers:: VirtualFlowers(FNode* symbol_fun,
				FNode* verticille,
				FNode* elements_number,
				FNode* color,
				FNode* top_dia,
				FNode* bottom_dia,
				FNode* length,
				FNode* alpha,
				FNode* beta)
: VirtualElements( symbol_fun, verticille, elements_number,
		  color, top_dia, bottom_dia, length, alpha, beta )
{
}

VirtualFlowers::~VirtualFlowers()
{
}
ostream& VirtualFlowers::displayOneLine(ostream& o) const
{
  o << "Virtual flowers. " << endl;

  return o;
}
char VirtualFlowers::getDefaultSymbol()
{
  return _dressingFile->getFlowerSymbol();
}

ValType VirtualFlowers::getDefaultAlpha()
{
  return _dressingFile->getDefaultFlowerAlpha()/_dressingFile->getAlphaUnit();
}

ValType VirtualFlowers::getDefaultBeta()
{
  return _dressingFile->getDefaultFlowerBeta()/_dressingFile->getAzimutUnit();
}

ValType VirtualFlowers::getDefaultLength()
{
  return _dressingFile->getDefaultFlowerLength()/_dressingFile->getLengthUnit();
}

ValType VirtualFlowers::getDefaultTopDia()
{
  return _dressingFile->getDefaultFlowerTopDia()/_dressingFile->getDiametersUnit();
}

ValType VirtualFlowers::getDefaultBottomDia()
{
  return _dressingFile->getDefaultFlowerBottomDia()/_dressingFile->getDiametersUnit();
}
