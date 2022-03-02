# !!!!!!! DO NOT CHANGE THE FORMATTING OR YOU'LL HAVE TO UPDATE fusion.rst !!!!!!!!!!!!!

# not shown in the documentation
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt


f = open("example_reconstruction_tips.py")
lines = f.readlines()
f.close()
eval( compile(reduce(lambda x,y: x+"\n"+y, lines[:34],""), "reconstr_plot_1", "exec") )


f, axarr = plt.subplots(2, 2)

axarr[0,0].set_title("image 0, slice 0")
axarr[0,0].imshow(im0[:,:,0], cmap=cm.Greys_r)

axarr[0,1].set_title("image 1, slice 0")
axarr[0,1].imshow(im1[:,:,0], cmap=cm.Greys_r)

h = im0.shape[2]/2
axarr[1,0].set_title("image 0, slice %d"%h)
axarr[1,0].imshow(im0[:,:,h], cmap=cm.Greys_r)

h = im1.shape[2]/2
axarr[1,1].set_title("image 1, slice %d"%h)
axarr[1,1].imshow(im1[:,:,h], cmap=cm.Greys_r)

