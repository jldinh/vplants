Functions
#########

:mod:`reech3d` 
=============

Description
===========

This function allows 2D or 3D image resampling using a 4x4 matrix. 
The value of a point in the result image is estimated : 
    * either by [bi|tri]linear interpolation,
    * or by using the value of the nearest point. 


Example
=======

.. code-block:: python
    :linenos:

    from vplants.asclepios import reech3d


:mod:`baladin` 
=============

Description
===========

This method is very similar to the ICP (Iterative Closest Point) algorithm, which consists in extracting feature points in the two images (say the reference and the floating images) to be registered and in iterating the following steps until convergence:

   1. to pair each feature point of the floating image with the closest feature point in the reference image,
   2. to compute the transformation that will best superimpose the paired points, and
   3. to apply this transformation to the feature points of the floating image.

Indeed, after applying the transformation, the pairings may have changed, thus a better transformation may be found by iterating these three steps.

To the opposite to the ICP algorithm, we do not extract feature points in the block matching algorithm but consider sub-images (i.e. blocks) in the floating image that will be paired to the most similar sub-image in the reference image. The computed transformation is the one that will best superimpose the centers of the paired sub-images. 

For more details, see  `Baladin: robust registration of images <http://www-sop.inria.fr/epidaure/software/Baladin/index.php>`_

Example
=======

.. code-block:: python
    :linenos:

    from vplants.asclepios import baladin


