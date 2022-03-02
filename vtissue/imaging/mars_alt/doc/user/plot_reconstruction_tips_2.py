# !!!!!!! DO NOT CHANGE THE FORMATTING OR YOU'LL HAVE TO UPDATE fusion.rst !!!!!!!!!!!!!

# not shown in the documentation
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt


f = open("example_reconstruction_tips.py")
lines = f.readlines()
f.close()
eval( compile(reduce(lambda x,y: x+"\n"+y, lines[:34],""), "reconstr_plot_2x", "exec") )

print altitude0

f, axarr = plt.subplots(2, 2)

axarr[0,0].set_title("Image 0 : Maximum Intensity Projection")
axarr[0,0].imshow(mip0[:,:,0], cmap=cm.Greys_r)

axarr[0,1].set_title("Image 1: Maximum Intensity Projection")
axarr[0,1].imshow(mip1[:,:,0], cmap=cm.Greys_r)

axarr[1,0].set_title("Image 0: Depth Map")
axarr[1,0].imshow(altitude0[:,:,0], cmap=cm.Greys_r)

axarr[1,1].set_title("Image 1 :Depth Map")
axarr[1,1].imshow(altitude1[:,:,0], cmap=cm.Greys_r)
