# Basic VTK pipeline

from pylab import *
from vtk import *


# ------- a boilerplate VTK pipeline ---------
#--- Create some LUTs
# (default) red -> blue (lo->hi)LUT
lutRedBlue = vtkLookupTable()
lutRedBlue.Build()

# blue -> red LUT
lutBlueRed = vtkLookupTable()
lutBlueRed.SetHueRange(0.667,0.0)
lutBlueRed.Build()


vtkRen=vtkRenderer()
vtkRenWin=vtkRenderWindow()

# TODO - allow changing window size
global winWidth, winHeight
winWidth = 256
winHeight = 256
vtkRenWin.SetSize(winWidth,winHeight)
im = zeros((winWidth,winHeight,3), typecode=Float)

vtkRenWin.OffScreenRenderingOn()
vtkRenWin.AddRenderer(vtkRen)

vtkRGB = vtkUnsignedCharArray()

"""
def copyVTKImage():
  vtkRenWin.Render()
  vtkRenWin.GetPixelData(0,0,winWidth-1,winHeight-1, 1,vtkRGB)
#  vtkRGB.Squeeze()
  idx=0
  for iy in range(winHeight-1,-1,-1):
    for ix in range(winWidth):
      im[iy,ix,0] = vtkRGB.GetValue(idx) / 255.
      im[iy,ix,1] = vtkRGB.GetValue(idx+1) / 255.
      im[iy,ix,2] = vtkRGB.GetValue(idx+2) / 255.
      idx += 3

def vtkRotX(degs):
  vtkRen.GetActiveCamera().Elevation(degs)

def vtkPerspective(flag):
  if flag > 0:
    vtkRen.GetActiveCamera().ParallelProjectionOff()
  else:
    vtkRen.GetActiveCamera().ParallelProjectionOn()

def vtkWinsize(w,h):
  winWidth = w
  winHeight = h
  im = zeros((winWidth,winHeight,3), typecode=Float)
  vtkRenWin.SetSize(winWidth,winHeight)
"""
