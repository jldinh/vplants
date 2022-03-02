#ifndef msStruct_h
#define msStruct_h

#ifdef _WIN32
#ifdef LGT_MAKEDLL  /* create a DLL library */
#define LGT_API  __declspec(dllexport)
#else               /* use a  DLL library */
#define LGT_API  __declspec(dllimport)
#endif
#else
#define LGT_API  
#endif


#include <string>
#include <vector>
#include <map>
#include <plantgl/tool/util_hashmap.h>
#include <plantgl/math/util_vector.h>
#include <plantgl/tool/util_array.h>
//#include <hash_map.h>
#include <plantgl/scenegraph/scene/scene.h>
#include <plantgl/scenegraph/scene/shape.h>
#include <plantgl/algo/base/bboxcomputer.h>
#include <plantgl/scenegraph/geometry/boundingbox.h>
#include <plantgl/gui/base/zbuffer.h>
#include <plantgl/gui/viewer/pglapplication.h>
//#include <plantgl/gui3/base/zbuffer.h>
//#include <plantgl/gui3/viewer/pglapplication.h>
/*
if qt4 is not available and qt3 is, gui3 must be used and changes in .h and .cpp are to be made :
PGLViewerApplication --> PGLViewerApplication3
ViewRayPointHitBuffer --> ViewRayPointHitBuffer3
RayPointHitList --> RayPointHitList3
*/

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace std;
using namespace STDEXT;


struct LGT_API iBeam //to ease the lenght retrival it was an dict{<x,y>:length}
{
long int id_x;
long int id_y;
float length;
};

LGT_API enum distrib {Turbid, Real};
LGT_API enum hull_choice {CvxHull, BdgSphere, BdgBox, BdgEllipse };

typedef vector<distrib> DistribVect;
typedef map<Vector3, map< DistribVect, float> > DirectionalDistribPMap;
typedef map<Vector3,float> DirectionalFloatMap;
typedef map<Vector3, vector<iBeam> > DirectionalHitBeamsMap;

class LGT_API msNode
{
private:
  long int id;
  long int scale;
  long int cplx;
  vector<long int>  components;
  float surface;
  float volume;
  ShapePtr shape;
  float globalOpacity;
  bool opak;

//directional datas should be stored in map or hashtable with direction as key

  DirectionalHitBeamsMap interceptedBeams;
  DirectionalFloatMap projSurface;
  DirectionalFloatMap glad;
  DirectionalDistribPMap pOmega;

public:


  msNode(long int);
  ~msNode();

  void setId( long int );
  void setScale( long int);
  void setCplx( long int );
  void addComponent(long int );
  void setComponents( const vector<long int>& );
  void setSurface( float );
  void setVolume( float );
  void setShape( ShapePtr sh );
  void setGlobalOpacity(float);
  void setOpak(bool);
  void addInterBeam( Vector3, iBeam );
  void setProjSurface( Vector3, float );
  void setGlad( Vector3, float );
  void setPOmega( Vector3, DistribVect, float );

  long int getId();
  long int getScale();
  long int getCplx();
  vector<long int> getComponents();
  float getSurface();
  float getVolume();
  ShapePtr getShape();
  float getGlobalOpacity();
  bool getOpak();
  float getBeamLength( Vector3, long int, long int );
  vector<float> getLengthDistrib(Vector3);
  vector<iBeam> * getIBeams(Vector3);
  float getProjSurface( Vector3 );
  float getGlad( Vector3 );
  float getPOmega( Vector3, DistribVect );

  float computeSurface();
  float computeVolume();
  void afficheInfo();
  void cleanMaps();
  float estimateGlad(Vector3);

};

/******************* scaledStruct *********************************/

class LGT_API scaledStruct
{
private:
  string plantName;
  vector<msNode *> nodeList;
  pgl_hash_map<long int, long int> scales;

public:
  scaledStruct(string);
  ~scaledStruct();
  
  string getName();
  void setName(string);
  long int depth();

  void addNode( msNode * );
  void setNodeList( const vector<msNode *>& );
  msNode * getNode( long int );
  vector<long int> getAtoms(long int);

  vector<long int> get1Scale( long int );
  long int countScale();
  void sonOf( long int, long int );
  void cleanNodes();

  ScenePtr genNodeScene(long int);
  ScenePtr genSelectScene() ;
  ScenePtr genScaleScene( long int );
  ScenePtr genGlobalScene();
  float totalLA( long int );
  vector< pair<uint32_t,double> >   computeProjections( Vector3 );
  void sprojToNodes(Vector3, vector< pair<uint32_t,double> > );

  ViewRayPointHitBuffer * computeBeams(Vector3, long int, long int, float);
  void beamsToNodes( Vector3, ViewRayPointHitBuffer * );
  float probaClassic(long int, Vector3);
  Array2<float> probaImage( long int, Vector3, vector<distrib>, uint32_t, uint32_t );
  float probaIntercept( long int, Vector3, vector<distrib> );
  float probaBeamIntercept( long int, Vector3, vector<distrib>, long int, long int );
  float starClassic( long int, Vector3);
  float star( long int, Vector3, vector<distrib>);
  float availight_node( long int, Vector3, ViewRayPointHitBuffer *, DistribVect );
  map<long int, float> availight( long int, Vector3, ViewRayPointHitBuffer *, DistribVect );
};

typedef pgl_hash_map< long int, vector<long int> > decompoMap;
typedef vector<decompoMap> dicoTable ;

LGT_API ScenePtr centerShapes( const ScenePtr& );
LGT_API BoundingBoxPtr getBBox( const ShapePtr& );
LGT_API BoundingBoxPtr getBBox( const ScenePtr& );
LGT_API scaledStruct * ssFromDict( string, ScenePtr&, const dicoTable&, hull_choice );

#endif
