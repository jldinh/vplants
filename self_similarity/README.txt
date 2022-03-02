====== Self_similarity ======

**Authors** : Anne-Laure Gaillard

**Institutes** : LaBRI

**Status** : Python package 

**License** : Cecill-C

**URL** : http://openalea.gforge.inria.fr

===== About =====

=== Description ===

Self_similarity is a set of tools to compute plant compression using
self-similarity properties.

Self_similarity package aims to:
  * Export to tulip format.
  * Several algorithms for tree compression.
  
=== Content ===

The self_similarity package contains :

  * Meta informations files (README.TXT, AUTHORS.TXT, LICENSE.TXT).
  * Installation file (setup.py).
  * Autobuild scripts (SConstruct, src/cpp/SConscript, src/wrapper/SConscript).
  //* C++ library (src/cpp, src/include).
  //* C++ wrappers example with boost.python (src/wrapper).
  * Python package (src/self_similarity).
  * Custom system configuration (options.py).

The dependencies between libraries are: tree_matching, mtg, aml.

=== Download ===

Go to http://gforge.inria.fr/frs/?group_id=79

=== Requirements ===

* Scons >= 0.96.93
* SconsX
* OpenAlea.Deploy
* Boost.Python


=== Installation ===

Self_similarity default installation command is:

For users, just type
<code>
python setup.py install
</code>

For developers, use
<code>
python setup.py develop
</code>

=== Utilisation ===

Use specific implementation help

===== Documentation =====
cf. ./doc/how_to.txt
