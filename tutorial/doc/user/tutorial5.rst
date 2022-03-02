Biomecanics on MTG
###################################

.. topic:: Section contents

    In this section, we introduce the `your thematic 
    <http://en.wikipedia.org/wiki/Machine_learning>`_
    vocabulary that we use through-out `vplants` and give a 
    simple example.


The problem setting
===================


Loading an example dataset
==========================

 The `tutorial` package comes with a few datasets. The data are in
 `share` directory. See the `data howto <>` 
 for more details.::

    >>> import vplants.tutorial
    >>> from openalea.deploy.shared_data import get_shared_data_path
    >>> print get_shared_data_path(vplants.tutorial, 'empty.txt')

Write your tutorial
====================


