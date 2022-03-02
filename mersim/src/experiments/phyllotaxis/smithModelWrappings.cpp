#include <boost/python.hpp>
#include "smithModel.hpp"

using namespace boost::python;

BOOST_PYTHON_MODULE(smithModel)
{
    class_<Model>("Model")
        .def("get_time", &Model::get_time)
        .def("set_time", &Model::set_time)
    ;
}
