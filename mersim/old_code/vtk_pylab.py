# matlab-like funcs using VTK, to be used in matplotlib
# Randy Heiland, Indiana University

from pylab import zeros
from vtk import *
from vtkPipe import *

meshActor = vtkActor()
plot3Actor = vtkActor()

def mesh(x,y,z, colored):
#  global zlo,zmax
  pts = vtkPoints()
  xlen = len(x[1])
  ylen = len(y)
  print 'xlen,ylen=',xlen,ylen
  print 'zsize=',size(z)
  pts.SetNumberOfPoints(size(z))
  idx = 0
  zlo = z[0,0]
  zmax = z[0,0]
  for iy in range(ylen):
    for ix in range(xlen):
      pts.SetPoint(idx, x[iy,ix], y[iy,ix], z[iy,ix])
      idx = idx + 1
      if z[iy,ix] < zlo:
        zlo = z[iy,ix]
      if z[iy,ix] > zmax:
        zmax = z[iy,ix]
  print 'zlo= ',zlo

  meshSG = vtkStructuredGrid()
  meshSG.SetDimensions(xlen,ylen,1)
  meshSG.SetPoints(pts)

  meshGeom = vtkStructuredGridGeometryFilter()
  meshGeom.SetInput(meshSG)

  if colored > 0:
    elev = vtkElevationFilter()
    elev.SetInput(meshGeom.GetOutput())
    pdnormals = vtkPolyDataNormals()
    pdnormals.SetInput(elev.GetPolyDataOutput())

  meshMapper = vtkPolyDataMapper()
  
  if colored > 0:
    meshLUT = vtkLookupTable()
    meshLUT.SetHueRange(lutBlueRed.GetHueRange())
    meshLUT.SetSaturationRange(lutBlueRed.GetSaturationRange())
    meshLUT.SetValueRange(lutBlueRed.GetValueRange())
    meshLUT.Build()

    meshMapper.SetInput(pdnormals.GetOutput())
    meshMapper.ScalarVisibilityOn()
    meshMapper.SetScalarRange(zlo,zmax)
    meshMapper.SetLookupTable(meshLUT)
    meshLUT.SetTableRange(zlo,zmax)
  else:
    meshMapper.SetInput(meshGeom.GetOutput())


  meshActor.SetMapper(meshMapper)
  vtkRen.AddActor(meshActor)


def plot3(x,y,z):
  pts = vtkPoints()
  vlen = len(x)
  print 'vlen=',vlen
  pts.SetNumberOfPoints(vlen)
  for idx in range(vlen):
    pts.SetPoint(idx, x[idx], y[idx], z[idx])
  print 'plot3 bounds= ',pts.GetBounds()

  # create a polyline (cellarray)
  pl = vtkCellArray()
  pl.InsertNextCell(vlen)
  for idx in range(vlen):
    pl.InsertCellPoint(idx)

  pd = vtkPolyData()
  pd.SetPoints(pts)
  pd.SetLines(pl)

  mapper = vtkPolyDataMapper()
  mapper.SetInput(pd)

  plot3Actor.SetMapper(mapper)
  plot3Actor.SetScale(1,1,0.1)
  vtkRen.AddActor(plot3Actor)

  # Create a text property for both cube axes
  tprop = vtkTextProperty()
  tprop.SetColor(1, 1, 1)
  tprop.ShadowOn()

  # rf. /home/heiland/VTK/Examples/Annotation/Python/cubeAxes.py
  axes = vtkCubeAxesActor2D()
  axes.SetInput(pd)
  axes.SetCamera(vtkRen.GetActiveCamera())
  axes.SetLabelFormat("%6.4g")
  axes.SetFlyModeToOuterEdges()
  axes.SetFontFactor(0.8)
  axes.SetAxisTitleTextProperty(tprop)
  axes.SetAxisLabelTextProperty(tprop)

#------------------------------------------------------------------
def vtkRender():
  vtkRenWin.Render()

def vtkClear():
# remove all actors hack
  vtkRen.RemoveActor(meshActor)
  vtkRen.RemoveActor(plot3Actor)
  return
  
def vtkImage():
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
#  vtkRen.GetActiveCamera().ComputeViewPlaneNormal()
  vtkRen.ResetCamera()
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
