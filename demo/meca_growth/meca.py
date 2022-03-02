from physics.mechanics import isotropic_material,TensorMechanics2D,UniformPressure2D
from celltissue.data import TPropertyMap
from celltissue.data.wisp_triangulation import FaceCloneMap
from celltissue.algo.growth import Meca2DGrowth

class MecaGrowth (object) :
	"""
	container for mechanical growth
	"""
	def __init__ (self, wt, thickness, P, fixed, nu, E, G, Gth, strain0) :
		self.wt=wt
		self.thickness=thickness
		self.P=P
		self.fixed=fixed
		self.nu=nu
		self.E=E
		self.G=G
		self.Gth=Gth
		self.strain0=strain0
		self.algo=None
	
	def material_map (self) :
		nu=self.nu
		mat=TPropertyMap(0,0.,((wid,isotropic_material(young,nu)) for wid,young in self.E.iteritems()))
		return mat
	
	def get_algo (self, dt) :
		wt=self.wt
		thick=FaceCloneMap(self.thickness,wt)
		self.algo=Meca2DGrowth(FaceCloneMap(self.material_map(),wt),
				thick,
				self.strain0,
				UniformPressure2D(wt,self.P,thick).forces(),
				self.fixed,
				FaceCloneMap(self.G,wt),
				self.Gth,
				dt)
		return self.algo

	def turgor_strain (self, wid) :
		"""
		return the computed strain in the meristem
		"""
		wt=self.wt
		faces=list(wt.wisp_to_faces(wid))
		surf=[wt.surface(fid) for fid in faces]
		strain=[self.algo.turgor_strain(fid) for fid in faces]
		tot=surf[0]*strain[0]
		for i in xrange(1,len(faces)) :
			tot+=surf[i]*strain[i]
		tot=(1./sum(surf))*tot
		return tot
	
	def turgor_stress (self, wid) :
		"""
		return the computed stress in the meristem
		"""
		wt=self.wt
		faces=list(wt.wisp_to_faces(wid))
		surf=[wt.surface(fid) for fid in faces]
		stress=[self.algo.turgor_stress(fid) for fid in faces]
		tot=surf[0]*stress[0]
		for i in xrange(1,len(faces)) :
			tot+=surf[i]*stress[i]
		tot=(1./sum(surf))*tot
		return tot

