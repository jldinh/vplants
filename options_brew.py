num_jobs=9
#qhull_lib='/Library/Python/2.6/site-packages/qhull-2003.1-py2.6-macosx-10.6-universal.egg/lib'
#qhull_includes='/Library/Python/2.6/site-packages/qhull-2003.1-py2.6-macosx-10.6-universal.egg/include'
QTDIR='/usr/local'
WITH_CGAL=True
WITH_MPFR=WITH_GMP=WITH_ANN=True
ann_includes='/usr/local/include'
ann_libpath='/usr/local/lib'
boost_includes=mpfr_includes=gmp_includes='/usr/local/include'
boost_lib=mpfr_libpath=gmp_libpath='/usr/local/lib'
qhull_libs_suffix='6'
boost_libs_suffix='-mt'
EXTRA_CCFLAGS='-DWITH_QHULL_2011 -DCGAL_CFG_NO_CPP0X_VARIADIC_TEMPLATES'
EXTRA_LINK_FLAGS='-F/usr/local/lib'
#gl_includes='/usr/X11/include'
