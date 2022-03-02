====================
Using of TIFF images
====================

This tutorial explains how to convert TIFF images into InrImage.

To convert TIFF images into InrImage, run : ::
    
    EMPILER "TIFF basename" "number of slices" "dimension X" "dimension Y" "0" "1X" "VX" "VY" "VZ" "0"
    mv ./total.inr.gz tot1Sub.inr.gz

The parameters used by EMPILER are : 

* **TIFF basename** : the name of TIFF images with the file extension stripped off. For example, ‘/home/user/images/plantB-1039.tif’ == ‘/home/user/images/plantB-10’
 
* **number of slices** : number of TIFF images

* **dimension X** : images width
 
* **dimension Y** : images height

* **1X** : 
    * X = 0 for unsigned char images
    * X = 1 for Red channel
    * X = 2 for Green channel
    * X = 3 for Blue channel

* **VX** : voxel size X 
* **VY** : voxel size Y
* **VZ** : voxel size Z 


