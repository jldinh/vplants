/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: Plant Graphic Library
 *
 *       Copyright 1995-2003 UMR Cirad/Inria/Inra Dap - Virtual Plant Team
 *
 *       File author(s): F. Boudon
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


#include "triangulation3D.h"

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

#ifdef WITH_CGAL
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Triangulation_vertex_base_with_info_3.h>
#include <CGAL/Delaunay_triangulation_3.h>
// #include <CGAL/Triangulation_3.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel         K;
typedef CGAL::Triangulation_vertex_base_with_info_3<uint32_t, K>    Vb;
typedef CGAL::Triangulation_data_structure_3<Vb>                    Tds;

typedef CGAL::Delaunay_triangulation_3<K, Tds>                      Triangulation;
// typedef CGAL::Triangulation_3<K,Tds>      Triangulation;


typedef Triangulation::Cell_handle    Cell_handle;
typedef Triangulation::Vertex_handle  Vertex_handle;
typedef Triangulation::Locate_type    Locate_type;
typedef Triangulation::Point          Point;
typedef Triangulation::Segment        Segment;



inline Point toPoint(const Vector3& v) { return Point(v.x(),v.y(),v.z()); }
inline Vector3 toVector3(const Point& v) { return Vector3(v.x(),v.y(),v.z()); }

#endif

Index3ArrayPtr 
PGL::delaunay_triangulation3D(const Point3ArrayPtr points)
{
#ifdef WITH_CGAL
    Triangulation triangulation;
    uint32_t pointCount = 0;
    for (Point3Array::const_iterator it = points->begin(); it != points->end(); ++it)
        triangulation.insert(toPoint(*it))->info() = pointCount++;

    Index3ArrayPtr result(new Index3Array(points->size()));
    for(Triangulation::Finite_facets_iterator it = triangulation.finite_facets_begin();
        it != triangulation.finite_facets_end(); ++it){
            const Cell_handle cell = it->first;
            const int& index = it->second;
	        const int index1 = cell->vertex(triangulation.vertex_triple_index(index, 0))->info();
	        const int index2 = cell->vertex(triangulation.vertex_triple_index(index, 1))->info();
	        const int index3 = cell->vertex(triangulation.vertex_triple_index(index, 2))->info();
            result->push_back(Index3(index1,index2,index3));
    } 
#else
    #ifdef _MSC_VER
    #pragma message("function 'delaunay_triangulation3D' disabled. CGAL needed.")
    #else
    #warning "function 'delaunay_triangulation3D' disabled. CGAL needed"
    #endif

    Index3ArrayPtr result;
#endif
    return result;
}
