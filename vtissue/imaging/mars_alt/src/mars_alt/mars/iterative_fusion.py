import os
import os.path
import sys
from openalea.image.all import imread, imsave
from vplants.mars_alt.mars.reconstruction import reconstruct, reconstruction_task
from vplants.mars_alt.mars.reconstruction import fuse_reconstruction
from openalea.image.spatial_image import SpatialImage

def iterative_fusion(images_path, initialisations, 
                     voxel_size = None, 
                     reference_image_index = 0, path_output = "./",
                     auto_linear_params = None, auto_non_linear_params = None,
                     iteration_number = 4,
                     intermediate_results = False):
    """
    Given a set of images, there associated initialisations
    and the parameters of linear and non linear transformation, 
    it apply recursively a given number of time the registration.

    If we have three images A, B and C
    it will make the registration of the images B and C on the image A.
    Then fuse those three registrered images in a high resolution image F.
    Then it will register the images A, B and C on the image F.
    Then fuse those images in a new high resolution image F'.
    And finally repeat this process as much time as asked by the user.

    :Parameters:
    - `images_path` (list [of 'str']) : list of paths of each image to treat, must be read by imread
    - `initialisations` (list [of 'numpy.ndarray']) : list of 4x4 matrices of transformation (output of the manual reconstruction for example). In most cases, the matrix linked to the reference image will be the 4x4 identity matrix
    - `voxel_size` (tuple (of 'float') ) : sometimes the resolution isn't defined in the image directly and needs to be manually write, None by default
    - `reference_image_index` ('int') : the index of the reference image in `images_path`, 0 by default
    - `path_output` ('str') : some temporary files need to be made, this is the path of where there will be create. It's also the path of where the intermediate images will be record. "./" by default
    - `auto_linear_params` (automatic_linear_parameters) : None by default
    - `auto_non_linear_params` (automatic_non_linear_parameters) : None by default
    - `iteration_number` ('int') : number of iteration. 4 by default
    - `intermediate_results` ('bool') : True if we want intermediate results, if True it will save the intermediate images in 'path_output' folder. False by default

    :Return:
    - `image_reference` (SpatialImage) : fused image after the iterations
    """
    
    # we need to have a as manual transformation as we have images
    assert(len(images_path) == len(initialisations))
    # check out if the path exists
    assert(os.path.exists(path_output))
    assert(path_output[-1]=='/')
    
    images = [imread(pth) for pth in images_path]
    reference_image = SpatialImage( images[reference_image_index].copy() )
    
    if isinstance(voxel_size, tuple) and (len(voxel_size)==3) :
        for im in images:
            im.resolution = voxel_size
    
    im_high_res_path=[]
    tasks = []
    # We apply the initialisation to each images
    for i, im in enumerate(images):
        task_tmp = reconstruction_task(reference_image, im, initialisation = initialisations[i])
        recons_task, recon_results = reconstruct([task_tmp])
        im_high_res_path.append(path_output+"tilted_"+str(i)+".inr.gz")
        imsave(path_output+"tilted_"+str(i)+".inr.gz", 
               SpatialImage(fuse_reconstruction(recons_task, recon_results, use_ref_im=False)))
        task = reconstruction_task(reference_image, im, initialisation = initialisations[i],
                                   auto_linear_params = auto_linear_params,
                                   auto_non_linear_params = auto_non_linear_params)
        tasks.append(task)
    
    
    recons_task, recon_results = reconstruct(tasks)
    reference_image = SpatialImage(fuse_reconstruction(recons_task, recon_results, use_ref_im=False))
    if intermediate_results:
        imsave(path_output+"fused_0.inr.gz", 
               reference_image)
    
    
    for i in range(iteration_number-1):
        tasks = []
        for im in enumerate(im_high_res_path):
            task = reconstruction_task(reference_image, im, initialisation = None,
                                       auto_linear_params = auto_linear_params,
                                       auto_non_linear_params = auto_non_linear_params)
            tasks.append(task) 
        recons_task, recon_results = reconstruct(tasks)
        reference_image = SpatialImage(fuse_reconstruction(recons_task, 
                                                           recon_results, 
                                                           use_ref_im=False))
        if intermediate_results:
            imsave(path_output+"fused_"+str(j+1)+".inr.gz", 
                   reference_image)
        
    return reference_image
