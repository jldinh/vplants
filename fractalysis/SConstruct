# -*-python-*-

from openalea.sconsx import config, environ
import os, fnmatch

ALEASolution = config.ALEASolution

pj= os.path.join

name='fractalysis'

options = Variables(['../options.py', 'options.py'], ARGUMENTS )
tools = ['boost_python', 'vplants.plantgl', 'qt4']

env = ALEASolution(options, tools)

# Set build directory
prefix= env['build_prefix']

env.Append( CPPPATH = pj( '$build_includedir','fractalysis' ) )

# Build stage
SConscript( pj(prefix,"src/cpp/SConscript"),
            exports={"env":env} )

SConscript( pj(prefix,"src/wrapper/SConscript"),
            exports={"env":env} )

Default("build")
