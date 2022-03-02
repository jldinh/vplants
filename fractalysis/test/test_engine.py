import openalea.fractalysis.engine as eng
import openalea.plantgl.all as pgl

vec = [ (1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1),(-1,1,1),(-1,1,-1),(-1,-1,1),(-1,-1,-1)]
box= pgl.Box((0.45,0.45,0.45))

cantor_dust = pgl.Scene()
for v in vec:
  cantor_dust.add( pgl.Shape( pgl.Translated(v,box) ) )

def test_computeGrid():
  res = eng.computeGrid(cantor_dust, 3)
  assert res[0] == 8, 'Intercepted voxels number should be 8 but is %d' % res[0]

def test_computeGrids():
  res = eng.computeGrids(cantor_dust, 5)
  assert res[0][0] == 8, 'Intercepted voxels number should be 8 but is %d' % res[0][0]
  assert res[-1][0] == 64, 'Intercepted voxels number should be 64 but is %d' % res[-1][0]

def test_MatrixLac_generation():
  pts = [[0, 0, 0], [0, 0, 1], [0, 0, 3], [0, 0, 4], [0, 1, 0], [0, 1, 1], [0, 1, 3], [0, 1, 4], [0, 3, 0], [0, 3, 1], [0, 3, 3], [0, 3, 4], [0, 4, 0], [0, 4, 1], [0, 4, 3], [0, 4, 4], [1, 0, 0], [1, 0, 1], [1, 0, 3], [1, 0, 4], [1, 1, 0], [1, 1, 1], [1, 1, 3], [1, 1, 4], [1, 3, 0], [1, 3, 1], [1, 3, 3], [1, 3, 4], [1, 4, 0], [1, 4, 1], [1, 4, 3], [1, 4, 4], [3, 0, 0], [3, 0, 1], [3, 0, 3], [3, 0, 4], [3, 1, 0], [3, 1, 1], [3, 1, 3], [3, 1, 4], [3, 3, 0], [3, 3, 1], [3, 3, 3], [3, 3, 4], [3, 4, 0], [3, 4, 1], [3, 4, 3], [3, 4, 4], [4, 0, 0], [4, 0, 1], [4, 0, 3], [4, 0, 4], [4, 1, 0], [4, 1, 1], [4, 1, 3], [4, 1, 4], [4, 3, 0], [4, 3, 1], [4, 3, 3], [4, 3, 4], [4, 4, 0], [4, 4, 1], [4, 4, 3], [4, 4, 4]]

  mat = eng.lactrix_fromScene(cantor_dust, 'cantorDust', 5, density=False)
  assert mat.dim == 3, 'Dimension should be 3 but is %d' % mat.dim
  assert mat.size == 5, 'Matrix size should be 5 but is %d' % mat.size
  assert mat.points == pts, 'Discrepencies in non-zero values'
  assert mat.vox_size == pgl.Vector3(0.584,0.584,0.584), 'Incorrect voxel size'

