#include <iostream>
#include <assert.h>
#include <math.h>

// #define LGT_MAKEDLL

#include <plantgl/tool/timer.h>
#include <plantgl/scenegraph/container/pointarray.h>
#include <plantgl/algo/base/discretizer.h>
#include <plantgl/algo/base/surfcomputer.h>
#include <plantgl/algo/base/volcomputer.h>

#include <plantgl/algo/fitting/fit.h>
#include <plantgl/scenegraph/transformation/translated.h>



using namespace std;

#include "fractalysis/light/msStruct.h"

msNode::msNode( long int s ):
 scale( s ),
 id( 0 ),
 cplx( 0 ),
 surface( 0 ),
 volume( 0 ),
 globalOpacity(-1),
 opak(false)
{/*
  scale = s;
  id = 0;
  cplx = 0;
  components = vector< long int>();
  surface = 0;
  volume = 0;
  interceptedBeams = DirectionalHitBeamsMap();
  projSurface =  DirectionalFloatMap();
  pOmega =  DirectionalFloatMap();*/
}

msNode::~msNode() {}

void msNode::setId( long int i) {id = i;}
void msNode::setScale( long int s) {scale = s;}
void msNode::setCplx( long int c ) {cplx = c; }
void msNode::addComponent( long int c )
{ 
  components.push_back( c ); 
}
void msNode::setComponents( const vector< long int>& v ) { components = v; }
void msNode::setSurface( float s ) { surface = s;}
void msNode::setVolume( float v ) { volume = v;}
void msNode::setShape( ShapePtr sh ) 
{
  shape = sh; 
  setSurface( computeSurface() );
  setVolume(  computeVolume() );
}

void msNode::setGlobalOpacity(float p) { globalOpacity = p;}

void msNode::setOpak(bool o) { opak = o;}

void msNode::addInterBeam( Vector3 v, iBeam ib )
{
  v.normalize();
  if( interceptedBeams.find( v ) == interceptedBeams.end() )
    {
      vector<iBeam> vect;
      vect.insert( vect.begin(), ib );
      //assert( vect.size() == 1 && vect.capacity() >= 1 && vect[0] == ib);
      interceptedBeams[ v ] = vect;
    }
  else
    {
       interceptedBeams[ v ].push_back( ib );
    }
}

void msNode::setProjSurface( Vector3 v, float s ) 
{
  v.normalize();
  projSurface[ v ] = s;
}

void msNode::setGlad( Vector3 v, float g ) 
{
  v.normalize();
  glad[ v ] = g;
}

void msNode::setPOmega( Vector3 v, DistribVect d, float po )
{
  v.normalize();
  map<Vector3, map< DistribVect, float> >::iterator pom_it= pOmega.find( v );
  if( pom_it != pOmega.end() ) //v already has pomega calculated
  {
    ( pom_it->second )[ d ] = po;
  }
  else
  {
    map<DistribVect, float> distribMap;
    distribMap[ d ] = po;
    pOmega[ v ] = distribMap;
  }
  //cout<<"POmega for node "<<getId()<<" is "<<po<<endl;
}

long int msNode::getId() { return id;}
long int msNode::getScale() {return scale;}
long int msNode::getCplx() {return cplx;}
vector< long int> msNode::getComponents() { return components; }
float msNode::getSurface() {return surface;}
float msNode::getVolume() {return volume;}
ShapePtr msNode::getShape() {return shape;}
float msNode::getGlobalOpacity() {return globalOpacity;}
bool msNode::getOpak() {return opak;}

vector<iBeam> * msNode::getIBeams(Vector3 v)
{
  DirectionalHitBeamsMap::iterator ibeams_it = interceptedBeams.find(v);
  if( ibeams_it != interceptedBeams.end())
    return &ibeams_it->second;
  else
  {
    vector<iBeam> * v = new vector<iBeam>();
    return  v;
  }
}

float msNode::getBeamLength( Vector3 v, long int x, long int y )
{
  v.normalize();
  if( interceptedBeams.find( v ) == interceptedBeams.end() )
  {
    //cout<<"getBeamLength : Direction was not computed or an error has occured, please report, nodeId : "<<getId()<<endl;
    return -1;
  }
  else
  {
    vector<iBeam> vect = interceptedBeams[ v ];
    for( vector<iBeam>::iterator iBeam_iter = vect.begin(); iBeam_iter != vect.end(); ++iBeam_iter )
    {
      if( iBeam_iter->id_x == x && iBeam_iter->id_y == y )
        { return iBeam_iter->length;}
    }
    return -1; //this beam does not intercept this node
  }
}

vector<float> msNode::getLengthDistrib(Vector3 v)
{
  vector<float> lDistrib;
  v.normalize();
  if( interceptedBeams.find( v ) == interceptedBeams.end() )
  {
    cout<<"Direction not computed"<<endl ;
    return lDistrib;
  }
  else
  {
    vector<iBeam> vect = interceptedBeams[ v ];
    for( vector<iBeam>::iterator iBeam_iter = vect.begin(); iBeam_iter != vect.end(); ++iBeam_iter )
    {
      lDistrib.push_back(iBeam_iter->length);
    }
    return lDistrib ;
  }
}

float msNode::getProjSurface( Vector3 v ) //return 0 if problem
{
  v.normalize();
  if( projSurface.find( v ) == projSurface.end() )
  {
    cout<<"getProjSurface : Direction was not computed or an error has occured, please report, nodeId : "<<getId()<<" direction : "<<v<<endl;
    return 0;
  }
  else
    { return projSurface[ v ]; }
}

float msNode::getGlad( Vector3 v ) //return 0 if problem
{
  v.normalize();
  if( glad.find( v ) == glad.end() )
  {
    float gl = estimateGlad(v);
    setGlad(v, gl);
  }
  return glad[ v ];
}

float msNode::getPOmega( Vector3 v, DistribVect d ) //return -1 if problem
{
  v.normalize();
  DirectionalDistribPMap::const_iterator pom_it= pOmega.find( v );
  if( pom_it == pOmega.end() ) //Direction does not exist
  {
    //cout<<"getPOmega : Direction was not computed or an error has occured, please report, nodeId : "<<getId()<<endl;
    return -1;
  }
  else
  {
    map<DistribVect, float>::const_iterator distri_it= ( pom_it->second ).find( d );
    if( distri_it == ( pom_it->second ).end() ) //Distribution does not exist for that direction
      {
        //cout<<"Distribution for this direction was not computed"<<endl;
        return -1;
      }
    else
    {
      //cout<<"Returning computed pomega"<<endl;
      return distri_it->second;
    }
  }
}

float msNode::computeSurface()
{
  Discretizer d;
  SurfComputer surfc( d );
  if( shape->apply( surfc ) )
    return surfc.getSurface();
}

float msNode::computeVolume()
{
  Discretizer d;
  VolComputer volc( d );
  if( shape->apply( volc ) )
    return volc.getVolume();
}

void msNode::afficheInfo()
{
  cout<<"Id : "<<getId()<<endl;
  cout<<"Scale : "<<getScale()<<endl;
  cout<<"Complex : "<<getCplx()<<endl;
  cout<<endl<<"Components : ";
  vector< long int> v = getComponents();
  for( vector< long int>::const_iterator vit = v.begin(); vit != v.end(); ++vit )
  {
    cout<< *vit<<" ";
  }
  cout<<endl;
  cout<<"Surface : "<<getSurface()<<endl;
  cout<<"Volume : "<<getVolume()<<endl;
  cout<<"#####################################################"<<endl;
}

void msNode::cleanMaps()
{
  interceptedBeams.clear();
  projSurface.clear();
  glad.clear();
  pOmega.clear();
}

float msNode::estimateGlad(Vector3 v)
{
  v.normalize();
  float error = 0.005, sum_p0 = 0, p0 = 0, len = 0, cvg = 0;
  float porosity = 1 - globalOpacity ;
  float glai = - log( porosity );
  float vol = getVolume();
  float my_glad = glai * getProjSurface(v) / vol;
  vector<float> ldis = getLengthDistrib(v);

  for (vector<float>::const_iterator beaml = ldis.begin(); beaml != ldis.end(); ++beaml)
  {
    sum_p0 += exp( - my_glad * (*beaml) );
  }
  p0 = sum_p0 / ldis.size();
  //cout<<"init p0 : "<< p0 <<endl;
  
  bool sup = p0 > porosity;
  float step = my_glad/20;
  while( fabs(p0 - porosity) > error && cvg < 1000 )
  {
    if (p0 > porosity)
    {
      if( !sup )
        step /= 2 ;
      sup = true;
      my_glad += step ;
    }
    else
    {
      if( sup )
        step /= 2;
      sup = false;
      my_glad -= step ;
      if( my_glad < 0)
        {
        sup = true;
        my_glad += step ;
        cout<<"Pb de passage dans le negatif"<<endl;
        }
    }
    sum_p0 = 0;
    for (vector<float>::const_iterator beaml = ldis.begin(); beaml != ldis.end(); ++beaml)
    {
      sum_p0 += exp( - my_glad * (*beaml) );
    }
    p0 = sum_p0 / ldis.size();
    //cout<<"p0 : "<< p0 <<endl;
    cvg++;
  }
  //cout<<"final p0 : "<< p0 <<endl;
  //cout<< "nbr de boucle pour convergence : "<<cvg<<endl ;
  if( cvg > 999 )
    cout<<"pb de convergence..."<<endl ;
  cout<<"\x0d"<<cvg<<" round to estimate GLAD for node "<<getId()<<" in direction "<<v<<" : "<<my_glad<<flush;
  return my_glad;
}

/******************* scaledStruct *********************************/

scaledStruct::scaledStruct( string plname )
{
  plantName = plname;
  nodeList = vector<msNode *>() ;
}

scaledStruct::~scaledStruct()
{
  for( int i = 0; i<nodeList.size(); i++ )
    delete nodeList[ i ];
}

string scaledStruct::getName() {return plantName;}
void scaledStruct::setName(string pln) {plantName = pln;}
long int scaledStruct::depth() {return scales.size();}

void scaledStruct::addNode( msNode * n ) { nodeList.push_back( n ); }
void scaledStruct::setNodeList(const vector<msNode *>& v ) { nodeList = v; }

msNode * scaledStruct::getNode( long int id )
{
  id--;
  if( id >=0 && id< nodeList.size() )
    return nodeList[ id ];
}

vector< long int> scaledStruct::getAtoms( long int id )
{
  msNode * n = getNode( id );
  vector< long int> atoms;
  vector< long int> compo = n->getComponents();
  if( compo.size() == 0 )
  {
    atoms.push_back( n->getId() );
  }
  else
  {
    for( int i=0; i<compo.size(); i++ )
    {
      vector< long int> v = getAtoms( compo[ i ] );
      for( int j = 0; j < v.size(); j++ )
        atoms.push_back( v[ j ] );
    }
  }
  //delete n;  fait une erreur de seg, pkoi ?
  return atoms;
}

vector< long int> scaledStruct::get1Scale( long int sc )
{
  vector< long int> v;
  msNode * n;
  for( int i=0; i < nodeList.size(); i++ )
  {
    n = nodeList[ i ];
    if( n->getScale() == sc )
      v.push_back( n->getId() );
    
  }
  return v;
}

long int scaledStruct::countScale()
{
  long int nbSc = 0;
  scales.clear();
  if( nodeList.size() > 0 )
  {
    for( int i=0; i<nodeList.size(); i++ )
    {
      msNode * n = nodeList[ i ];
      if( n->getScale() > 0 )
      {
        if( scales.find( n->getScale() ) == scales.end() )
          scales[ n->getScale() ] = 1;
        else
          scales[ n->getScale() ] += 1;
      }
    }

  pgl_hash_map< long int, long int>::iterator mit;
  for( mit = scales.begin(); mit != scales.end(); mit++ )
    {
      cout<<"Scale "<<mit->first<<" : "<<mit->second<<endl;
      nbSc++;
    }
  }
  else
  {
    cout<<"Node must be defined first"<<endl;
  }
  return nbSc;
}

void scaledStruct::sonOf( long int comp, long int cplx )
{
  getNode( comp )->setCplx( cplx );
  getNode( cplx )->addComponent( comp );
} 

void scaledStruct::cleanNodes()
{
  for(int i=0; i<nodeList.size(); ++i)
  {
    nodeList[i]->cleanMaps();
  }
}

ScenePtr scaledStruct::genNodeScene( long int id )
{
  ScenePtr scene = new Scene();
  vector< long int> list = getAtoms( id );
  msNode * n;
  for( int i=0; i<list.size(); ++i )
  {
    n = getNode( list[ i ] );
    scene->add( n->getShape() );
  }
  n = getNode( id );
  if( n->getComponents().size() != 0 )
    scene->add( n->getShape() );
  return scene; 
}

ScenePtr scaledStruct::genSelectScene()
{
  vector<uint32_t> sel = PGLViewerApplication::getSelection();
  ScenePtr scene = new Scene();
  for ( int i=0; i<sel.size(); ++i )
  {
    ScenePtr sc = genNodeScene( sel[ i ] );
    for( Scene::const_iterator sc_it = sc->getBegin(); sc_it != sc->getEnd(); ++sc_it )
    {
      scene->add( * sc_it );
    }
  }
  return scene;
}

ScenePtr scaledStruct::genScaleScene( long int sc)
{
  ScenePtr scene = new Scene();
  vector< long int> vect = get1Scale( sc );
  msNode * node;
  for( int i=0; i<vect.size(); ++i )
  {
    node = getNode( vect[ i ] );
    scene->add( node->getShape() );
  }
  node = NULL;
  delete node;
  return scene;
}

ScenePtr scaledStruct::genGlobalScene()
{

  ScenePtr scene = new Scene();
  for(int i=0; i<depth(); i++)
  {
    //scene->merge(genScaleScene(i+1));
    scene->merge(genScaleScene(depth() - i));
  }
  return scene;
}

float scaledStruct::totalLA( long int id )
{
  vector< long int> leaves = getAtoms( id );
  float leafArea = 0;
  for( int i=0 ; i<leaves.size(); ++i )
    leafArea += getNode( leaves[ i ] )->getSurface();

  return leafArea;
}

vector< pair<uint32_t,double> >  scaledStruct::computeProjections( Vector3 v )
{
  Timer t;
  t.start();
  //setting the camera according to scene size
  v.normalize();
  
  PGLViewerApplication::animation( true );
  PGLViewerApplication::glFrameOnly( true );
  PGLViewerApplication::resize(600,600);
  PGLViewerApplication::setOrthographicCamera ();
  PGLViewerApplication::setGrid (false, false, false, false);
  PGLViewerApplication::display( genScaleScene( 1 ) );
  PGLViewerApplication::glFrameSize( 600,600 ); //size can be changed...
  //camera is set, doing the projections
  vector< pair<uint32_t,double> > proj, total;
  vector< pair<uint32_t,double> >::const_iterator it_proj;
  ScenePtr sc ;
  BoundingBoxPtr bbox;
  Vector3 bb_center, cam_pos;
  pgl_hash_map< long int, long int>::iterator mit;
  msNode * node;
  for( mit = scales.begin(); mit != scales.end(); mit++ )
  {
    sc = centerShapes( genScaleScene( mit->first ) );
    cout<<"Projecting scale "<<mit->first<<endl;
    bbox = getBBox(  sc );
    if( bbox == NULL )
      {
      cout<<"Bbox problem"<<endl;
      bbox = new BoundingBox( Vector3( -500,-500,-500 ), Vector3( 500,500,500 ) ); //default bbox
      }
    bb_center = bbox->getCenter();
    float bb_factor = max( max(bbox->getXRange(), bbox->getYRange()), bbox->getZRange() );
    cam_pos = bb_center + v*-3*bb_factor;
    //cout<<"Camera pos : "<<cam_pos<<"  looking at : "<<bb_center<<endl;
    PGLViewerApplication::lookAt(cam_pos, bb_center );
    PGLViewerApplication::display( sc );
    proj = PGLViewerApplication::getProjectionSizes( sc );
    
    for( it_proj = proj.begin(); it_proj != proj.end(); ++it_proj )
    {
      total.push_back( *it_proj);
      node = getNode( it_proj->first );
      node->setProjSurface( v, it_proj->second );
    }
  }
  t.stop();
  cout<<"Projections computed in "<<t.elapsedTime()<<"s"<<endl;
  node = NULL;
  delete node;
  return total;
}

void scaledStruct::sprojToNodes(Vector3 v, vector< pair<uint32_t,double> > sproj)
{
  msNode * node;
  v.normalize();
  for( vector< pair<uint32_t,double> >::const_iterator it_sproj = sproj.begin(); it_sproj != sproj.end(); ++it_sproj )
  {
    node = getNode( it_sproj->first );
    node->setProjSurface( v, it_sproj->second );
  }
  node = NULL;
  delete node;
}

ViewRayPointHitBuffer * scaledStruct::computeBeams(Vector3 direction, long int width, long int height, float d_factor)
{

  Timer t;
  t.start();
  direction.normalize();
  ScenePtr globalScene = genGlobalScene();
  BoundingBoxPtr bbox = getBBox(globalScene);
  Vector3 bb_center, cam_pos;

  bb_center = bbox->getCenter();
  float bb_factor = max( max(bbox->getXRange(), bbox->getYRange()), bbox->getZRange() );
  cam_pos = bb_center + direction*(-bb_factor)*d_factor;

  PGLViewerApplication::animation( true );
  PGLViewerApplication::glFrameOnly( true );
  PGLViewerApplication::resize(width,height);
  PGLViewerApplication::setOrthographicCamera ();
  PGLViewerApplication::setGrid (false, false, false, false);
  PGLViewerApplication::display( globalScene );
  PGLViewerApplication::lookAt(cam_pos, bb_center );
  PGLViewerApplication::glFrameSize( width, height ); //size can be changed...
  ViewRayPointHitBuffer * beams = PGLViewerApplication::castRays2( globalScene, true);
  t.stop();
  cout<<"Beams computed in "<<t.elapsedTime()<<"s"<<endl;
  beamsToNodes( direction, beams);
  //PGLViewerApplication::glFrameOnly( false );
  return beams;
}

void scaledStruct::beamsToNodes( Vector3 direction, ViewRayPointHitBuffer * beams )
{
  direction.normalize();
  long int nbLign = beams->getColsSize();
  long int nbCol = beams->getRowsSize();
  RayPointHitList::iterator raypointhit_it;
  msNode * node;
  iBeam ib ;
  for( int lgn=0; lgn< nbLign; ++lgn )
  {
    for( int col=0; col<nbCol; ++col )
    {
      RayPointHitList oneBeam = beams->getAt( lgn, col );
      for( raypointhit_it=oneBeam.begin(); raypointhit_it!=oneBeam.end(); ++raypointhit_it )
      {
        node = getNode( raypointhit_it->id );
        ib.id_x = lgn; 
        ib.id_y = col;
        ib.length = norm(raypointhit_it->zmax - raypointhit_it->zmin);
        node->addInterBeam( direction, ib );
      }
    }
  }
  node = NULL;
  delete node;
}

float scaledStruct::probaClassic( long int node_id, Vector3 direction)
{
  
  msNode * node = getNode(node_id);
  float vol = node->getVolume();
  float opac;
  direction.normalize();
  vector<iBeam> * interBeams = node->getIBeams(direction);
  long int beta = interBeams->size();
  if (beta>0)
  {
    float som=0;
    vector< long int> leaves_id = getAtoms(node_id);
    vector<float> leaves_sproj;
    for(int i=0; i<leaves_id.size(); ++i)
    {
      leaves_sproj.push_back(getNode(leaves_id[i]) -> getProjSurface(direction));
    }
    /*
    Recuperer le vecteur de toutes les feuilles : getAtoms
    faire pour chq rayon une boucle sur ces feuilles en faisant le produit des
    1-sproj(feuille) x (*ibeams_it).length/node->getVolume
    sommer tous les 1-produit
    renvoyer le tout pour le calcul du starClassic
    faire la fonction starClassic
    */
    float l, prod;
    long int s;
    vector<iBeam>::const_iterator ibeams_it ;
    for(ibeams_it = interBeams->begin(); ibeams_it != interBeams->end(); ++ibeams_it)
    {
      l = (*ibeams_it).length;
      prod=1;
      s = 0;
      //for(int s=0; s<leaves_sproj.size(); ++s)
      while( s < leaves_sproj.size() && prod > 0.)
      { 
        opac = l*leaves_sproj[s]/vol;
        if( opac > 1)
          opac = 1;
        prod*=(1 - opac); //assuming that leaves are opaque thus pOmega=1
        ++s;
      }
      som += (1-prod);
    }
    node = NULL;
    delete node;
    assert(som/beta <= 1);
    return som/beta;
  }
  else
  {
    cout<<"node "<<node_id<<" not intercepted by any beam -_-"<<endl;
    return 0;
  }
}

Array2<float> scaledStruct::probaImage( long int node_id, Vector3 direction, vector<distrib> distribution, uint32_t width, uint32_t height )
{
  Timer t;
  t.start();
  Array2<float> picture(width, height, 0);
  msNode * node = getNode(node_id);
  direction.normalize();
  assert((scales.size() - node->getScale()) == distribution.size() && 
          "Distribution size must be scales size - 1");
  assert(node->getComponents().size() > 0);
  
  vector<iBeam> * interBeams = node->getIBeams(direction);
  long int beta = interBeams->size();
  if(! beta > 0)
    cout<<"No beams for node "<<node->getId()<<" at scale "<<node->getScale()<<endl; 
  assert(beta>0 && "intercepted beam list must not be empty");
  float som=0;
  float pixOmega;
  vector<iBeam>::const_iterator ibeams_it ;
  for(ibeams_it = interBeams->begin(); ibeams_it != interBeams->end(); ++ibeams_it)
  {
    pixOmega= probaBeamIntercept( node_id, direction, distribution, (*ibeams_it).id_x, (*ibeams_it).id_y);
    som += pixOmega;
    picture.setAt((*ibeams_it).id_x, (*ibeams_it).id_y, pixOmega);
  }
  //cout<<"from probaImage "<<node_id<<"  som : "<<som<<"   beta : "<<beta<<endl;
  node->setPOmega(direction, distribution, som/beta);
  t.stop();
  cout<<"image and star computed in "<<t.elapsedTime()<<"s"<<endl;
  node = NULL;
  delete node;
  return picture;
}


float scaledStruct::probaIntercept( long int node_id, Vector3 direction, DistribVect distribution )
{
  msNode * node = getNode(node_id);
  direction.normalize();
  assert(scales.size() - node->getScale() == distribution.size()) ;
          //&& "Distribution size must be scales size - 1");
  if(node->getComponents().size() == 0)
    { 
      if(node->getGlobalOpacity() != -1)
        return node->getGlobalOpacity();
      else
        return 1; //leaves are condidered opaque for now
    }
  else
  {
    float proba = node->getPOmega(direction, distribution);
    if( proba >= 0)
      return proba;
    else //distribution not computed
    {
      vector<iBeam> * interBeams = node->getIBeams(direction);
      long int beta = interBeams->size();
      //assert(beta>0 && "intercepted beam list must not be empty");
      if(beta > 0)
      {
        float som=0;
        vector<iBeam>::const_iterator ibeams_it ;
        for(ibeams_it = interBeams->begin(); ibeams_it != interBeams->end(); ++ibeams_it)
        {
          som += probaBeamIntercept( node_id, direction, distribution, (*ibeams_it).id_x, (*ibeams_it).id_y);
        }
        //cout<<node_id<<"  som : "<<som<<"   beta : "<<beta<<endl;
        assert(som/beta <= 1);
        node->setPOmega(direction, distribution, som/beta);
        return som/beta;
      }
      else
      {
        cout<<"node "<<node_id<<" not intercepted by any beam -_-"<<endl;
        node->setPOmega(direction, distribution, 0);
        return 0; //not intercepted, thus opacity = 0
      }
    }
  }
  node = NULL;
  delete node;
}


float scaledStruct::probaBeamIntercept( long int node_id , Vector3 direction, vector<distrib> distribution, long int x_beamId, long int y_beamId)
{
  msNode * node = getNode(node_id);
  direction.normalize();
  assert(scales.size() - node->getScale() == distribution.size() && "Distribution size must be scales size - 1");
  distrib local_distrib;
  if(distribution.size() == 0 ) //should be leaf case or last scale
    {
      assert(node->getComponents().size() == 0 && "last scale can't have components or distrib too short"); //leaf case
      if(node->getGlobalOpacity() != -1)
        {
          if(node->getOpak())
            return node->getGlobalOpacity();
          else //beam travel distance taken into account
            {
              //cout<<"Node "<<node->getId()<<endl;
              float beam_length = node->getBeamLength(direction, x_beamId, y_beamId);
              //cout<<"beam length : "<<beam_length<<endl;
              float est_glad = node->getGlad(direction);
              //cout<<"glad is estimated : "<<est_glad<<endl;
              float val = 1 - exp(- est_glad * beam_length);
              if( val < 0 )
                cout<<"val : "<<val<<endl;
              return val ;
            }
        }
      else
        {
          //cout<<"\x0d"<<"that is a leaf : "<<node->getId()<<" scale "<<node->getScale()<<flush;
          return 1;
        }
    }
  else
  {
    local_distrib = distribution.front(); //contain the local distribution
    distribution.erase(distribution.begin()); //shorter by one to send to finer scale
  } 

  /*************************  Real distribution  *****************************************/
  if(local_distrib == Real)
  {
    bool intercept = false;
    float prod =1;
    vector< long int> compo =node->getComponents(); 
    long int c = 0;
    //for(int c=0; c<compo.size(); ++c)
    while( c < compo.size() && prod > 0.)
    {
      msNode * x = getNode(compo[c]);
      float beam_length =x->getBeamLength(direction, x_beamId, y_beamId);
      if( beam_length >= 0) //test pour savoir si intercepte par rayon ? a revoir
      {
        intercept = true;
        prod *= (1 - probaBeamIntercept(x->getId(), direction, distribution, x_beamId, y_beamId));
      }
      ++c ;
    }
    if(intercept)
      {
        //assert(1-prod >= 0);
        if(1-prod >= 0)
          return 1-prod;
        else
          {
            cout<< "bad value : "<< 1-prod << endl;
            return 1;
          }
      }
    else
      return 0;
  }

  /************************* Turbid distribution  ****************************************/
  else if(local_distrib == Turbid)
  {
    float length = node->getBeamLength(direction, x_beamId, y_beamId);
    if(length <= 0)
      length = 0;
    float prod=1;
    float px, sproj, opac ;
    vector< long int> compo =node->getComponents();
    long int c = 0;
    //for(int c=0; c<compo.size(); ++c)
    while( c < compo.size() && prod > 0.)
    {
      msNode * x = getNode(compo[c]);
      sproj = x->getProjSurface(direction);
      if(sproj == 0)
      {
        //computeProjections(direction);
        cout<<"node without sproj : "<<x->getId()<<endl;
        x -> setProjSurface(direction, 0.001);
        //sproj = x->getProjSurface(direction);
      }
      px = probaIntercept(x->getId(), direction, distribution);
      opac =  ( sproj * length * px) / node->getVolume() ;
      if(opac > 1)
        opac = 1;
      prod *= (1 - opac);
      ++c ;
    }
    assert(1-prod >= 0);
    /*
    if(1-prod < 0)
      {
        cout<<"p0 problem for node "<<node_id<<" : "<<prod<<endl;
        return 0;
      }
    */
    return 1-prod;
  }
  node = NULL;
  delete node;
}

float scaledStruct::starClassic( long int node_id, Vector3 direction) //needs to be called after having computed the intercepted beams
{
  Timer t;
  t.start();
  msNode * node = getNode(node_id);
  direction.normalize();
  float pomega, somega, surfaceFoliaire;
  somega = node->getProjSurface(direction);
  if(somega == 0)
  { 
    computeProjections(direction);
    somega = node->getProjSurface(direction);
  }
  surfaceFoliaire = totalLA(node_id); //totalLA doit faire attention si les elements sont des volumes --> /2
  pomega = probaClassic(node_id, direction);

  t.stop();
  cout<<"\x0d"<<"Classic star computed in "<<t.elapsedTime()<<"s"<<flush;
  node = NULL;
  delete node;
  return somega * pomega / surfaceFoliaire;

}

float scaledStruct::star( long int node_id, Vector3 direction, vector<distrib> distribution)
{
  //Timer t;
  //t.start();
  msNode * node = getNode(node_id);
  direction.normalize();
  float pomega, somega, surfaceFoliaire;
  somega = node->getProjSurface(direction);
  if(somega == 0)
  { 
    computeProjections(direction);
    somega = node->getProjSurface(direction);
  }
  surfaceFoliaire = totalLA(node_id);
  //should try to get it from node, if not compute it
  pomega = node->getPOmega(direction, distribution);

  if(pomega < 0)
    pomega = probaIntercept(node_id, direction, distribution);

  //t.stop();
  //cout<<"star computed in "<<t.elapsedTime()<<"s"<<endl;
  node = NULL;
  delete node;
  return somega * pomega / surfaceFoliaire;
}

map<long int, float> scaledStruct::availight( long int scale, Vector3 direction, ViewRayPointHitBuffer * beams, DistribVect distrib)
{
  Timer t;
  t.start();
  map<long int, float> result;
  vector<long int> nodes_id = get1Scale(scale); 
  for(vector<long int>::const_iterator scit = nodes_id.begin(); scit != nodes_id.end(); ++scit)
  {
    long int node_id = *scit;
    result[node_id] = availight_node( node_id, direction, beams, distrib);
  }
  t.stop();
  cout<<"Available light computed in "<<t.elapsedTime()<<"s"<<endl;
  return result;
}

float scaledStruct::availight_node( long int node_id, Vector3 direction, ViewRayPointHitBuffer * beams, DistribVect distrib)
{
  msNode * nother;
  msNode * node = getNode(node_id);
  RayPointHitList::iterator raypointhit_it;
  long int x, y;
  float beam_power, node_pos, nother_pos, vol, length, pom, pomega;
  float totalight = 0.0;

  direction.normalize();
  vector<iBeam> * interBeams = node->getIBeams(direction);
  long int beta = interBeams->size();
  //cout<<"Nombre de rayon interceptes : "<<beta<<endl;
  if (beta>0)
  {
    vector<iBeam>::const_iterator ibeams_it ;
    for(ibeams_it = interBeams->begin(); ibeams_it != interBeams->end(); ++ibeams_it)
    {
      x = (*ibeams_it).id_x;
      y = (*ibeams_it).id_y;

      //cout<<"computing beam id ["<<x<<","<<y<<"]"<<endl;
      beam_power = 1;
      RayPointHitList oneBeam = beams->getAt( x, y );
      raypointhit_it=oneBeam.begin();
      while( raypointhit_it->id != node_id && raypointhit_it != oneBeam.end() )
      {
        ++raypointhit_it;
      }
      if( raypointhit_it != oneBeam.end() )
      {
        node_pos = raypointhit_it->zmax*direction ;

        raypointhit_it=oneBeam.begin();
        if(node->getScale() == depth()) //leaf scale case
        {
          while( raypointhit_it!=oneBeam.end() && beam_power > 0)
          {
            nother = getNode( raypointhit_it->id );
            nother_pos = raypointhit_it->zmax*direction;
            if( (nother->getScale() == node->getScale()) && (node_pos > nother_pos) )
              beam_power = 0; //there is another leaf intercepting beam before
            ++raypointhit_it;
          }
        }
        else
        {
          while( raypointhit_it!=oneBeam.end() && beam_power > 0 )
          {
            nother = getNode( raypointhit_it->id );
            nother_pos = raypointhit_it->zmax*direction;
            if( (nother->getScale() == node->getScale()) && (node_pos > nother_pos) )
            {
              if (node_pos - nother_pos > nother->getBeamLength(direction, x, y))
                length = nother->getBeamLength(direction, x, y);
              else //intersection between the two enveloppes
                length = node_pos - nother_pos;
              vol = nother->getVolume();
              assert(vol > 0);
              pom =  nother->getPOmega(direction, distrib);
              if( pom > 0 && pom <= 1)
                pomega = pom * (length *nother->getProjSurface(direction))/vol; //distrib qui va bien, avoir
              else
                cout<<"problem with stored POmega : "<<pom<<endl;
                pomega = 1;

              beam_power *= (1 - pomega);
            }
            ++raypointhit_it;
          }
        }
        totalight += beam_power;
      }
      else
        cout<<"intercepted beam("<<x<<","<<y<<") does not intercept node ["<<node_id<<"] !!!"<<endl;
    }
    //return (totalight/beta); // ratio of received onto possible
    return (totalight/beta)*node->getProjSurface(direction); //quantity of Energie
  }
  else
    return 0;
}

/***************************************************************************************/
/*                          End of classes definition                                  */
/***************************************************************************************/
ScenePtr centerShapes( const ScenePtr& scene )
{
  ScenePtr ctrd_sc = new Scene();
  ShapePtr old_sh, new_sh;
  TranslatedPtr tr;
  BoundingBoxPtr bbox;
  for( Scene::iterator sc_it = scene->getBegin(); sc_it != scene->getEnd(); ++sc_it )
  {
    old_sh = dynamic_pointer_cast<Shape>( * sc_it );
    bbox = getBBox( old_sh );
    tr = new Translated( bbox->getCenter()*-1, old_sh->getGeometry() );
    new_sh = new Shape( GeometryPtr( tr ), old_sh->getAppearance(), old_sh->getId() );
    ctrd_sc->add( new_sh );
  }
  return ctrd_sc;
}

BoundingBoxPtr getBBox( const ShapePtr& shape )
{
  Discretizer d;
  BBoxComputer bbc( d );

  if( shape->apply( bbc ) )//true means bboxcomputer went ok
    return bbc.getBoundingBox ( );
  else
    return NULL;
}

BoundingBoxPtr getBBox( const ScenePtr& scene )
{
  Discretizer d;
  BBoxComputer bbc( d );

  if( bbc.process(scene) )//true means bboxcomputer went ok
    return bbc.getBoundingBox ( );
  else
    return NULL;
}


scaledStruct * ssFromDict( string sceneName, ScenePtr& scene, const dicoTable& dt, hull_choice h_choice )
{
  Timer t;
  t.start();
  pgl_hash_map< long int, long int> idList; // contains all scene ids, id shape are uint32, does it matter ?
  long int pos =0; //position de la shape dans la scene
  for( Scene::iterator sc_it = scene->getBegin(); sc_it != scene->getEnd(); ++sc_it )
  {
    idList[ ( *sc_it )->getId() ]= pos++ ;
  }
  pgl_hash_map< long int, long int> old2new;
  vector<msNode *> nodeList;
  long int nodeListCount =0;
  msNode * node;
  for( int i=0; i<dt.size(); i++ ) //for each scale
  {
    long int s = dt.size() - i; //scale from smallest (dt.size()) to largest (1)
    decompoMap scaleMap = dt[ s-1 ];
    for( decompoMap::iterator dcm_it = scaleMap.begin(); dcm_it!=scaleMap.end(); dcm_it++ ) // for each component
    {
      node = new msNode( s );
      node->setId( ++nodeListCount );
      nodeList.push_back( node );

      if( s == 1 ) //the root, should be unique
        node->setCplx( -1 ); //-1 mean no Cplx

      vector< long int> subelmt = dcm_it -> second;
      for( int sb=0; sb<subelmt.size(); ++sb ) //for each sub element
      {
        bool leaf = false;
        long int idx; //idList index of target id in case of leaf = shape index in scene
        //int idl =0;
        pgl_hash_map< long int, long int>::const_iterator idl_it=idList.find( subelmt[ sb ] ) ;
        if( idl_it != idList.end() )
          {
            leaf =true;
            idx =idl_it->second;
          }
        if( leaf )
        {
          msNode * leaf = new msNode( s+1 );
          leaf->setId( ++nodeListCount );
          nodeList.push_back( leaf );
          ShapePtr scShape = dynamic_pointer_cast<Shape>( scene->getAt( idx ) );
          ShapePtr leafShape = new Shape( scShape->getGeometry(), scShape->getAppearance(), leaf->getId() );
          leaf->setShape( leafShape );
          leaf->setCplx( node->getId() ); //embeded in python addComponent method
          node->addComponent( leaf->getId() );
        }
        else  //it is not a leaf
        {
          pgl_hash_map< long int, long int>::const_iterator o2n_it = old2new.find( subelmt[ sb ] );
          if( o2n_it != old2new.end() )
          {
            node->addComponent( o2n_it->second );
            nodeList[ o2n_it->second - 1 ]->setCplx( node->getId() );
          }
        }
      }
      //if( dcm_it->first != node->getId() )
      //  old2new[ dcm_it->first ] = node->getId();
      old2new[ dcm_it->first ] = node->getId();
      ShapePtr cvxhull = new Shape();
      
      /*
      cvxhull must be the convex hull of all node's component shape
      */
      Point3ArrayPtr pointList = new Point3Array();
      Discretizer d;
      vector< long int> compo = node->getComponents();
      for( int i=0; i<compo.size(); ++i )
        {
          if( nodeList[ compo[ i ] - 1 ]->getShape()->apply( d ) ) //true if discretization is ok
            {
              Point3ArrayPtr shapePoints = d.getDiscretization()->getPointList();
              ( * pointList )+=( * shapePoints );
            }
        }
      Fit f;
      f.setPoints( pointList );
      GeometryPtr hull ;
      switch( h_choice )
      {
        case CvxHull:
          hull = f.convexHull();
          break;
        case BdgSphere :
          hull = f.bsphere();
          break;
        case BdgBox :
          hull = f.balignedbox();
          break;
        case BdgEllipse :
          hull = f.bellipsoid();
          break;
        default:
          cout << "Sorry, '" << h_choice << "' does not correspond to an existing option. Please try again with either CvxHull, Sphere or Box.\n\n";
      }
      if( hull )
      {
        cvxhull->getGeometry() = hull; 
        AppearancePtr ap = nodeList[ compo[ 0 ] -1 ]->getShape()->getAppearance();
        cvxhull->getAppearance() = ap;
        node->setShape( cvxhull );
      }
      else
      {
        cout<<"Convex hull of "<< node ->getId() <<" not computed"<<endl;
        return NULL; //pas boooooooo
      }
    }
  }
  for( int i=0; i<nodeList.size(); ++i )
  {
    msNode * n = nodeList[ i ];
    n->getShape()->id = n ->getId();
  }
  scaledStruct * ss = new scaledStruct( sceneName );
  ss->setNodeList( nodeList );
  ss->countScale();
  t.stop();
  cout<<"scaledStructure generated in : "<<t.elapsedTime()<<"s"<<endl;
  node = NULL;
  delete node;
  return ss;
}
