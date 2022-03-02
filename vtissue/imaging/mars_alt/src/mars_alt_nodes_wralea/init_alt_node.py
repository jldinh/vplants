def init_alt(im1,im2,points1,points2,new_points1,new_points2):
    from copy import deepcopy
    if new_points1 is None: 
        return deepcopy(im1),deepcopy(im2),deepcopy(points1),deepcopy(points2)
    else : 
        return deepcopy(im1),deepcopy(im2),deepcopy(new_points1),deepcopy(new_points2)
