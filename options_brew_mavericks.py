num_jobs=8

# if qhull installed from brew, with default Qt :
qhull_libs_suffix='.6'
qhull_lib='/usr/local/Cellar/qhull/2012.1/lib'
qhull_includes='/usr/local/Cellar/qhull/2012.1/include'

QTDIR='/usr/local'
WITH_CGAL=True
WITH_MPFR=WITH_GMP=WITH_ANN=True
ann_includes='/usr/local/include'
ann_libpath='/usr/local/lib'
boost_includes=mpfr_includes=gmp_includes='/usr/local/include'
boost_lib=mpfr_libpath=gmp_libpath='/usr/local/lib'
boost_libs_suffix='-mt'

EXTRA_CCFLAGS='-stdlib=libc++ -fno-inline -DWITH_QHULL_2011 -DCGAL_CFG_NO_CPP0X_VARIADIC_TEMPLATES -DCGAL_EIGEN3_ENABLED -I/usr/local/Cellar/eigen/3.2.0/include/eigen3'
EXTRA_LINK_FLAGS='-F/usr/local/lib'

# If X11 has been installed manually :
gl_includes='/usr/X11/include'

def complete_path(path):
	import os

	def find_version_dir(path):
		exts = os.listdir(path)
		def mycmp(a,b):
		   a = map(int,a.split('.'))
		   b = map(int,b.split('.'))
		   for ai,bi in zip(a,b):
		   	  if ai == bi: continue
		   	  return cmp(ai,bi)
		   return 0
		exts.sort(mycmp)
		return exts[0]
	prefix,suffix = path.split('/VERSION/')
	return os.path.join(prefix,find_version_dir(prefix),suffix)

bison_bin=complete_path('/usr/local/Cellar/bison2/VERSION/bin')

flex_bin=complete_path('/usr/local/Cellar/flex/VERSION/bin')
flex_libpath=complete_path('/usr/local/Cellar/flex/VERSION/lib')
flex_include=complete_path('/usr/local/Cellar/flex/VERSION/include')

