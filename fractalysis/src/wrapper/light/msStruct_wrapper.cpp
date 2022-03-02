#include <light/msStruct.h>
#include <boost/python.hpp>

//GEOM_USING_NAMESPACE
PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace boost::python;
using namespace std;

/******************************************************************************************
***                          Structure Xchange                                          ***
******************************************************************************************/
template<class T>
boost::python::list vect2List( const T& vec )
{
  boost::python::list l;
  for(size_t vit = 0; vit < vec.size(); ++vit )
    l.append( vec[ vit ] );
  return l;
}

/*
template<class K>
template<class K,V>
boost::python::dict map2dict( const map<const K&, const V&>& mymap)
{
  boost::python::dict dico;
  for(map< K, V >::const_iterator mit = mymap.begin(); mit != mymap.end(); ++mit)
    dico[mit->first] = mit->second;
  return dico;
}
*/

template<class T>
vector<T> list2vec( boost::python::list l ){
  vector<T> array;
  object iter_obj = boost::python::object( handle<>( PyObject_GetIter( l.ptr() ) ) );
  while( 1 )
    {
    object obj; 
    try 
      { 
      obj = iter_obj.attr( "next" )();
      }
    catch( error_already_set ){ PyErr_Clear(); break; }
    T val = boost::python::extract<T>( obj );
    array.push_back( val );
    }
  return array;
}

dicoTable * pySc2Cpp( boost::python::list l ) //scale description as list of dictionnaries
{
  dicoTable * dt =new dicoTable();
  object iter_obj = boost::python::object( handle<>( PyObject_GetIter( l.ptr() ) ) );
  while( 1 )
    {
      object obj; 
      try 
      { 
        obj = iter_obj.attr( "next" )();
      }
      catch( error_already_set )
      {
        PyErr_Clear(); 
        break; 
      }
      //here begin the show...
      decompoMap oneScale;
      boost::python::dict oneSc = boost::python::extract<boost::python::dict>( obj );
      object iter_map_key = oneSc.iterkeys();
      object iter_map_val = oneSc.itervalues();
      while( 1 )
      {
        object obj_key, obj_val;
        try
        {
          obj_key = iter_map_key.attr( "next" )();
          obj_val = iter_map_val.attr( "next" )();
        }
        catch( error_already_set )
        {
          PyErr_Clear();
          break;
        }
        long int cplx = boost::python::extract< long int>( obj_key );
        boost::python::list l2 = boost::python::extract<boost::python::list>( obj_val );
        vector< long int> components = list2vec< long int>( l2 );
        oneScale[ cplx ] = components;
      }
      dt->push_back( oneScale );
    }
  return dt;
}

template<class T>
boost::python::list array2List( const T& matrix )
{
  boost::python::list mat;
  for(uint32_t line = 0; line < matrix.getRowsNb(); ++line )
  {
    boost::python::list l;
    for(uint32_t clmn = 0; clmn < matrix.getColsNb(); ++clmn )
      l.append( matrix.getAt(line, clmn) );
    mat.append(l);
  }
  return mat;
}


ViewRayPointHitBuffer * list_to_raybuf(  boost::python::list l )//beams structure from python to C++
{
  //iteration over lines
  object iter_list = boost::python::object( handle<>( PyObject_GetIter( l.ptr() ) ) );
  vector< vector<RayPointHitList> > ray_array;
  while( 1 )
  {
    object obj_line; 
    try 
      { obj_line = iter_list.attr( "next" )(); }
    catch( error_already_set )
      {
        PyErr_Clear(); 
        break; 
      }
    boost::python::list line = boost::python::extract<boost::python::list>( obj_line );
    //iteration over columns wich are beams
    object iter_line = boost::python::object( handle<>( PyObject_GetIter( line.ptr() ) ) );
    vector<RayPointHitList> ray_line;
    while( 1 )
      {
        object obj_col;
        try
          { obj_col = iter_line.attr( "next" )(); }
        catch( error_already_set )
          {
            PyErr_Clear();
            break;
          }
        boost::python::list col = boost::python::extract<boost::python::list>( obj_col );
        //iteration inside beam list that represent each hit
        object iter_col = boost::python::object( handle<>( PyObject_GetIter( col.ptr() ) ) );
        RayPointHitList beam;
        while( 1 )
          {
            object obj_hit;
            try
              { obj_hit = iter_col.attr( "next" )(); }
            catch( error_already_set )
              {
                PyErr_Clear();
                break;
              }
            boost::python::tuple hit = boost::python::extract<boost::python::tuple>( obj_hit );
            long int id = boost::python::extract< long int>( hit[ 0 ] );
            Vector3 zmin = boost::python::extract<Vector3>( hit[ 1 ] );
            Vector3 zmax;
            try
              {zmax = boost::python::extract<Vector3>( hit[ 2 ] ); }
            catch( error_already_set )
              {
                PyErr_Clear();
                zmin = zmax;
              }
            RayPointHit ray_hit( id, zmin, zmax );

            beam.push_back( ray_hit );
          }
        ray_line.push_back( beam );
      }
    ray_array.push_back( ray_line );
  }
  size_t nbLines = ray_array.size();
  if( nbLines == 0 )
    cout<<"there was a problem during python list iteration"<<endl;
  size_t nbCols = ray_array[ 0 ].size();
  ViewRayPointHitBuffer * all_beams = new ViewRayPointHitBuffer( nbLines ,  nbCols  );
  for( long int i=0; i<nbLines; ++i )
    {
      vector<RayPointHitList> array_line = ray_array[ i ]; //should test if nbCols == array_line.size()
      for( long int j=0; j<nbCols; ++j )
        {
          all_beams->getAt( i,j ) = array_line[ j ];
        }
    }
  return all_beams;
}

boost::python::object raybuf_to_list(ViewRayPointHitBuffer * buf) //beams structure from C++ to python
{
  boost::python::list res;
  for(size_t i = 0; i < buf->getColsSize();i++){
    boost::python::list row;
    for(size_t j = 0; j < buf->getRowsSize();j++){
      boost::python::list zlist;
      for(size_t k = 0; k < buf->getAt(i,j).size();k++){
        RayPointHit& inter = buf->getAt(i,j)[k];
        if(std::fabs(norm(inter.zmax-inter.zmin))<GEOM_EPSILON)
          zlist.append(make_tuple(inter.id,inter.zmin,inter.zmin));
        else zlist.append(make_tuple(inter.id,inter.zmin,inter.zmax));
      }
      row.append(zlist);
    }
    res.append(row);
  }
  return res;
}

boost::python::object sproj_to_list(vector< pair<uint32_t, double> > sp)
{
  boost::python::list sproj;
  for(size_t i=0; i<sp.size(); ++i)
  {
    sproj.append(make_tuple(sp[i].first, sp[i].second));
  }
  return sproj;
}

vector< pair<uint32_t, double> > list_to_sproj(boost::python::list l)
{
  vector< pair<uint32_t, double> > sproj;
  object iter_obj = boost::python::object( handle<>( PyObject_GetIter( l.ptr() ) ) );
  while( 1 )
  {
    object obj; 
    try 
    { 
      obj = iter_obj.attr( "next" )();
    }
    catch( error_already_set )
    { 
      PyErr_Clear(); 
      break; 
    }
    boost::python::tuple val = boost::python::extract<boost::python::tuple>( obj );
    uint32_t id = boost::python::extract<uint32_t>( val[0] );
    double surface = boost::python::extract<double>( val[1] );
    pair<uint32_t, double> p(id, surface);
    sproj.push_back(p);
  }
  return sproj;
}

vector<distrib> list2distrib( boost::python::list l ) //list describing organisation within scales
{
  vector<distrib> distribution;
  object iter_obj = boost::python::object( handle<>( PyObject_GetIter( l.ptr() ) ) );
  while( 1 )
    {
    object obj; 
    try 
      { 
      obj = iter_obj.attr( "next" )();
      }
    catch( error_already_set ){ PyErr_Clear(); break; }
    string val = boost::python::extract<string>( obj );
    distrib d;
    //if(val=="U")
    if(val=="R")
      d = Turbid;
    //else if(val =="R")
    else if(val =="A")
      d = Real;
    else
    {
      cout<<"Unknown distribution information, using Real"<<endl;
      d = Real;
    }
    distribution.push_back( d );
    }
  /*
  cout<<"C++ distrib : ";
  for(vector<distrib>::const_iterator dit = distribution.begin(); dit != distribution.end(); ++dit)
  {
    cout<<" "<<*dit<<" ";
  }
  cout<<endl;
  */
  return distribution;
}

boost::python::dict intFloatMap2dict( const map<long int, float>& mymap)
{
  boost::python::dict dico;
  for(map< long int, float >::const_iterator mit = mymap.begin(); mit != mymap.end(); ++mit)
    dico[mit->first] = mit->second;
  return dico;
}
/******************************************************************************************
***                          wrapping of msNode                                         ***
******************************************************************************************/

boost::python::object pyGetComponents(msNode * node)
{
  return vect2List( node->getComponents() );
}

void pySetComponents(msNode * node, boost::python::list l)
{
 node->setComponents( list2vec< long int>(l)); //ajouter dans msNode
}

void pyAddInterBeam( msNode * node, Vector3 dir, long int beam_x, long int beam_y, float l )
{
  iBeam ib;
  ib.id_x = beam_x;
  ib.id_y = beam_y;
  ib.length = l;
  node->addInterBeam( dir, ib );
}

boost::python::object pyGetLengthDistrib(msNode * node, Vector3 dir)
{
  return vect2List( node->getLengthDistrib(dir) );
}

void pySetPOmega(msNode * node, Vector3 dir, boost::python::list l, float po)
{
  node->setPOmega(dir, list2distrib(l), po);
}

float pyGetPOmega( msNode * node, Vector3 dir, boost::python::list l)
{
  return node->getPOmega(dir, list2distrib(l));
}

void classMsNode(){
        class_<msNode>("msNode",init< long int >("node for multiscaled structure",args( "scale" )))
            .add_property("id", &msNode::getId, &msNode::setId)
            .add_property("scale", &msNode::getScale, &msNode::setScale)
            .add_property("cplx", &msNode::getCplx, &msNode::setCplx )
            .add_property("surface", &msNode::getSurface, &msNode::setSurface )
            .add_property("volume", &msNode::getVolume, &msNode::setVolume )
            .add_property("globalOpacity", &msNode::getGlobalOpacity, &msNode::setGlobalOpacity )
            .add_property("opak", &msNode::getOpak, &msNode::setOpak )
            .add_property("shape", &msNode::getShape, &msNode::setShape )
            .add_property( "components", &pyGetComponents, &pySetComponents )
            .def("addComponent", &msNode::addComponent)
            .def("setPOmega", &pySetPOmega)
            .def( "getPOmega", &pyGetPOmega )
            .def( "getLengthDistrib", &pyGetLengthDistrib )
            .def("setProjSurface", &msNode::setProjSurface)
            .def( "getProjSurface", &msNode::getProjSurface )
            .def("setGlad", &msNode::setGlad )
            .def( "getGlad", &msNode::getGlad )
            .def( "addInterBeam", &pyAddInterBeam )
            .def( "getBeamLength", &msNode::getBeamLength )
            .def( "cout", &msNode::afficheInfo )
            .def( "cleanMaps", &msNode::cleanMaps )
            .def( "estimateGlad", &msNode::estimateGlad )
        ;

}

/******************************************************************************************
***                      wrapping of scaledStruct                                       ***
******************************************************************************************/

boost::python::object pyGetAtoms( scaledStruct * ss, long int id )
{ return vect2List( ss->getAtoms( id ) );}

boost::python::object pyGet1Scale( scaledStruct * ss, long int sc )
{ return vect2List( ss->get1Scale( sc ) );}

void pySetNodeList(scaledStruct * ss, boost::python::list l)
{ ss->setNodeList(list2vec<msNode *>(l)) ;}

boost::python::object pyComputeProjections(scaledStruct * ss, Vector3 v)
{ return sproj_to_list(ss->computeProjections(v));}

void pySprojToNodes(scaledStruct * ss, Vector3 v, boost::python::list sproj)
{ ss->sprojToNodes(v, list_to_sproj(sproj));}

boost::python::object pyComputeBeams(scaledStruct * ss, Vector3 v, long int width, long int height, float d_factor)
{ return raybuf_to_list(ss->computeBeams(v, width, height, d_factor));}

void pyBeamsToNodes( scaledStruct * ss, Vector3 v, boost::python::list l)
{ ss->beamsToNodes(v, list_to_raybuf(l)); }

boost::python::object pyProbaImage(scaledStruct * ss, long int nid, Vector3 direction, boost::python::list distribution, long int width, long int height)
{ return array2List(ss->probaImage(nid, direction, list2distrib(distribution), width, height));}

float pyProbaIntercep(scaledStruct * ss, long int nid, Vector3 direction, boost::python::list distribution)
{ return ss->probaIntercept(nid, direction, list2distrib(distribution));}

float pyProbaBeamIntercep(scaledStruct * ss, long int nid, Vector3 direction, boost::python::list distribution, long int x, long int y)
{ return ss->probaBeamIntercept(nid, direction, list2distrib(distribution), x, y);}

float pyStar(scaledStruct * ss, long int nid, Vector3 direction, boost::python::list distribution)
{ return ss->star(nid, direction, list2distrib(distribution));}

float pyAvailightNode( scaledStruct * ss, long int nid, Vector3 direction, boost::python::list beams, boost::python::list distribution)
{return ss->availight_node(nid, direction, list_to_raybuf(beams), list2distrib(distribution));}

boost::python::object pyAvailight( scaledStruct * ss, long int scale, Vector3 direction, boost::python::list beams, boost::python::list distribution)
{
  return intFloatMap2dict( ss->availight(scale, direction, list_to_raybuf(beams), list2distrib(distribution)) );
}

void classScaledStruct()
{
    class_<scaledStruct>( "scaledStruct",init<string >("multi scale structure using msNode",args( "name" )) )
        .add_property("name", &scaledStruct::getName, &scaledStruct::setName)
        .add_property("depth", &scaledStruct::depth)
        .def( "addNode", &scaledStruct::addNode )
        .def( "getNode", &scaledStruct::getNode, return_value_policy<reference_existing_object>() )
        .def( "getAtoms", &pyGetAtoms )
        .def( "get1Scale", &pyGet1Scale )
        .def( "setNodeList", &pySetNodeList )
        .def( "countScale", &scaledStruct::countScale )
        .def( "cleanNodes", &scaledStruct::cleanNodes )
        .def( "sonOf", &scaledStruct::sonOf )
        .def( "genNodeScene", &scaledStruct::genNodeScene )
        .def( "genSelectScene", &scaledStruct::genSelectScene )
        .def( "genScaleScene", &scaledStruct::genScaleScene )
        .def( "genGlobalScene", &scaledStruct::genGlobalScene )
        .def( "computeProjections", &pyComputeProjections )
        .def( "sprojToNodes", &pySprojToNodes )
        .def( "computeBeams", &pyComputeBeams )
        .def( "beamsToNodes", &pyBeamsToNodes )
        .def( "totalLA", &scaledStruct::totalLA )
        .def( "probaClassic", &scaledStruct::probaClassic )
        .def( "probaImage", &pyProbaImage )
        .def( "probaIntercept", &pyProbaIntercep )
        .def( "probaBeamIntercept", &pyProbaBeamIntercep )
        .def( "star", &pyStar )
        .def( "starClassic", &scaledStruct::starClassic )
        .def( "availightNode", &pyAvailightNode )
        .def( "availight", &pyAvailight )
    ;
}


/******************************************************************************************
***                                External methods                                     ***
******************************************************************************************/

scaledStruct * pySsFromDict( string scn, ScenePtr& sc, boost::python::list l, string h_choice  )
{
  dicoTable * dico = pySc2Cpp( l );
  hull_choice hc ;
  if( h_choice == "Box")
    hc = BdgBox;
  else if ( h_choice == "Sphere")
    hc = BdgSphere;
  else if ( h_choice == "Ellipse")
    hc = BdgEllipse;
  else
    hc = CvxHull;
  scaledStruct * res = ssFromDict( scn, sc, *dico, hc );
  delete dico;
  return res;
}

BOOST_PYTHON_MODULE(_light)
    {
      classMsNode();
      classScaledStruct();
      def( "ssFromDict", &pySsFromDict, return_value_policy<reference_existing_object>()  );
      def( "centerShapes", &centerShapes );
    }


