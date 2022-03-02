/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: The Plant Graphic Library
 *
 *       Copyright 1995-2007 UMR CIRAD/INRIA/INRA DAP 
 *
 *       File author(s): F. Boudon et al.
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

#ifndef __export_list_h__
#define __export_list_h__

#include <boost/python.hpp>
#include <vector>
#include <plantgl/tool/util_hashmap.h>
#include "exception.h"

/* ----------------------------------------------------------------------- */
template <class T>
struct make_object {
	typedef T obj_type;

    const obj_type& __c_obj;

    make_object(const T& c_obj) : __c_obj(c_obj) {}
    boost::python::object operator()() const { return boost::python::object(__c_obj); }
};

template <class Iterator, class Translator>
static boost::python::object list_convert(Iterator beg, Iterator end)  {
        boost::python::list l;
        for (Iterator it = beg; it != end; ++it)
            l.append(Translator(*it)());
        return l;
    }

template <class T, class Translator = make_object<typename T::value_type> >
struct list_converter {
    typedef T list_type;
    typedef typename T::const_iterator list_const_iterator;
    typedef typename T::value_type list_element_type;

    list_const_iterator __c_list_begin;
    list_const_iterator __c_list_end;

    list_converter(const T& c_list): __c_list_begin(c_list.begin()),__c_list_end(c_list.end()){}
    list_converter(const list_const_iterator& c_list_begin,
              const list_const_iterator& c_list_end): 
            __c_list_begin(c_list_begin),__c_list_end(c_list_end){}


    inline boost::python::object convert() const { return list_convert<list_const_iterator,Translator>(__c_list_begin,__c_list_end); }
    inline boost::python::object operator()() const { return convert(); }
    inline operator boost::python::object () const { return convert(); }
};

template <class T, class Translator>
list_converter<T,Translator> make_list(const T& c_list) { return list_converter<T,Translator>(c_list); }

template <class T>
list_converter<T> make_list(const T& c_list) { return list_converter<T>(c_list); }

template<class T>
list_converter<T, list_converter<typename T::value_type> > 
make_list_of_list(const T& l){
    return list_converter<T, list_converter<typename T::value_type> >(l);
}

/* ----------------------------------------------------------------------- */

template <class T, class Translator = make_object<typename T::value_type> >
struct tuple_converter {
	typedef T list_type;
    typedef typename T::const_iterator list_const_iterator;
    typedef typename T::value_type list_element_type;

    list_const_iterator __c_list_begin;
    list_const_iterator __c_list_end;

    tuple_converter(const T& c_list): __c_list_begin(c_list.begin()),__c_list_end(c_list.end()){}
    tuple_converter(const list_const_iterator& c_list_begin,
              const list_const_iterator& c_list_end): 
            __c_list_begin(c_list_begin),__c_list_end(c_list_end){}

	inline boost::python::object convert() const {
		return boost::python::tuple(list_convert<list_const_iterator,Translator>(__c_list_begin,__c_list_end)); 
	}
	inline boost::python::object operator()() const { return convert(); }
	inline operator boost::python::object () const { return convert(); }
};

template <class T, class Translator>
tuple_converter<T> make_pgl_tuple(const T& c_tuple) { return tuple_converter<T,Translator>(c_tuple); }

template <class T>
tuple_converter<T> make_pgl_tuple(const T& c_tuple) { return tuple_converter<T>(c_tuple); }

/* ----------------------------------------------------------------------- */

template <class T, 
          class KeyTranslator = make_object<typename T::key_type>, 
#if (defined(USING_UNORDERED_MAP)) || defined(WIN32_STL_EXTENSION)
          class ValueTranslator = make_object<typename T::mapped_type>
#else
          class ValueTranslator = make_object<typename T::data_type>
#endif
         ,
#if (defined(USING_UNORDERED_MAP)) || defined(WIN32_STL_EXTENSION)
          class ValueType = typename T::mapped_type
#else
          class ValueType = typename T::data_type
#endif
         >
struct dict_converter {
	typedef T dict_type;
    typedef typename T::const_iterator dict_const_iterator;
    typedef typename T::key_type dict_key_type;
    typedef ValueType dict_value_type;

    dict_const_iterator __c_dict_begin;
    dict_const_iterator __c_dict_end;

    dict_converter(const T& c_dict): __c_dict_begin(c_dict.begin()),__c_dict_end(c_dict.end()){}
    dict_converter(const dict_const_iterator& c_dict_begin,const dict_const_iterator& c_dict_end): 
        __c_dict_begin(c_dict_begin),__c_dict_end(c_dict_end){}

    boost::python::object convert() const {
        boost::python::dict d;
        for (dict_const_iterator it = __c_dict_begin; it != __c_dict_end; ++it)
            d[KeyTranslator(it->first)()] = ValueTranslator(it->second)();
        return d;
    }
	inline boost::python::object operator()() const { return convert(); }
	inline operator boost::python::object () const { return convert(); }
};

template <class T, class KeyTranslator, class ValueTranslator>
dict_converter<T,KeyTranslator,ValueTranslator> make_dict(const T& c_dict) 
{ return dict_converter<T,KeyTranslator,ValueTranslator>(c_dict); }

template <class T, class KeyTranslator>
dict_converter<T,KeyTranslator> make_dict(const T& c_dict) 
{ return dict_converter<T,KeyTranslator>(c_dict); }

template <class T>
dict_converter<T> make_dict(const T& c_dict) 
{ return dict_converter<T>(c_dict); }


template<class T, class U>
inline boost::python::object make_pair_tuple(const std::pair<T,U>& value) { return boost::python::make_tuple(value.first, value.second); }

#endif


/* ----------------------------------------------------------------------- */
