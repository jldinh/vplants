# -*- python -*-
#
#       vplants.mars_alt.alt.tissuVirtuel
#
#       Copyright 2010-2011 INRIA - CIRAD - INRA - ENS-Lyon
#
#       File author(s): Vincent Mirabet
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################


__license__= "TBD"
__revision__=" $Id$ "

#check that this version takes voxelsizes into account.

import sys, string
import math
from math import *
from vtk import *
import Tkinter
import vtk

#from aide import *

class tissuVirtuel(object):
	"""
	this function converts CELLGRAPH output into vtk file.
	this version calculates cells independently
	SYNTAX :
		to convert entire structure :
			essaisConversionGraph.py input(.txt) output.vtk 1
		to convert subpart specified by a sphere
			essaisConversionGraph.py input(.txt) output.vtk 2 row col plane diameter
		to convert subpart specified by a cell list
			essaisConversionGraph.py input(.txt) output.vtk 3 Id1 Id2 Id3 ....

	"""
	def __init__(self,fich="",vtk1="",param="4",liste=[]):
		self.__verbose=0
		self.nom=fich
		self.param=param
		self.liste=liste
		self.cell_face={}
		self.cell_identite={}
		self.cell_cell={}
		self.face_cell={}
		self.cell_barycentre={}
		self.cell_volume={}
		self.cell_layer={}
		self.face_edge={}
		self.face_triangle={}
		self.edge_vertex={}
		self.vertex_coord={}

		self.cell_vtkTrianglesJoined={}
		self.cell_vtkVertexJoined={}
		self.cell_vtkPolyDataJoined={}
		self.cell_vtkTrianglesSep={}
		self.cell_vtkVertexSep={}
		self.cell_vtkPolyDataSep={}

		self.vx, self.vy, self.vz=[],[],[]

		self.cell_marqueur={}
		self.cell_auxine={}
		self.face_pin={}

		self.vtkSep=vtkPolyData()
		self.vtkJoin=vtkPolyData()
		self.vtkLabels=[]

                self.vtkcell_face={}
		self.vtkcell_cell={}

		if fich!="":

			print "let's see what we do with file : "+fich

			try:
				self.cell_face, self.cell_barycentre, self.cell_volume, self.cell_layer, self.face_edge, self.edge_vertex, self.vertex_coord, self.vx, self.vy, self.vz = self.ouvrir2(fich)
			except IOError:
				print "Oops!  wrong input file specified, try again"
				sys.exit(1)
			#print "		success!\n"

			#print "	trying trianguler"
			self.face_triangle=self.trianguler()
			#print "		success!\n"
			#print "	trying definirFaceCell"
			self.definirFaceCell()
			#print "		success!\n"
			#print "	trying definirCellCell"
			self.definirCellCell()
			self.createVtkLabels()
			#print "		success!\n"
			if param=="4":
				self.liste=self.definitionListe1(liste)
			if param=="3":
				self.liste=self.definitionListe3(liste)

			self.getVTK()
			self.remplirDicosVides()
			self.setDataCell(self.cell_identite, "identite")
			self.setDataCell(self.cell_volume, "volume")
			self.convertVtk()
		else:
			print "attention pas de fichier grapheMeristeme dans la classe mere"

	def getVTK(self):
		self.convertVtkJoined()
		self.convertVtkSep()
		self.createVtkLabels()


	def remplirDicosVides(self):
		"""
		on remplit les dicos vides pour qu'ils aient les bonnes clefs
		"""
		for i in self.cell_volume.keys():
			self.cell_auxine[i]=[]
			self.cell_identite[i]=i

	def definirCellCell(self):
		"""
		cette fonction a pour but de creer le lien cellule -- cellule
		"""
		for c in self.cell_face.keys():
			self.cell_cell[c]=[]
			for f in self.cell_face[c]:
				for c1 in self.face_cell[f]:
					if c1 != c:
						self.cell_cell[c].append(c1)
			self.cell_cell[c]=list(set(self.cell_cell[c]))


	def definirFaceCell(self):
		"""
		cette fonction a pour but de definir le lien face -- cellule
		"""
		for f in self.face_edge.keys():
			self.face_cell[f]=[]

		for c in self.cell_face.keys():
			for f in self.cell_face[c]:
				self.face_cell[f].append(c)

		for f in self.face_cell.keys():
			l=self.face_cell[f]
			l=list(set(l))
			self.face_cell[f]=l

		for f in self.face_cell.keys():
			if len(self.face_cell[f])>2:
				print "la face %s a plus de deux cellules voisines",f

	def trianguler(self):
		"""
		fonction pour creer des tas de triangles
		"""
		face_triangle={}

		for f in self.face_edge.keys():
			face_triangle[f]=[]
			x,y,z=0.0,0.0,0.0
			vertex=[]
			for e in self.face_edge[f]:
				for v in self.edge_vertex[e]:
					vertex.append(v)
			#print vertex
			#on supprime les doublons
			vertex=list(set(vertex))
			#print vertex
			for v in vertex:
				x+=self.vertex_coord[v][0]
				y+=self.vertex_coord[v][1]
				z+=self.vertex_coord[v][2]
			if len(vertex)>0:
				x=x/len(vertex)
				y=y/len(vertex)
				z=z/len(vertex)
			else:
				x,y,z=-1,-1,-1

			i=0
			for e in self.face_edge[f]:
				triangle=[]
				triangle.append([x,y,z])
				if len(self.edge_vertex[e])==2:
					for c in self.edge_vertex[e]:
						xc, yc, zc=self.vertex_coord[c][0], self.vertex_coord[c][1], self.vertex_coord[c][2]
						triangle.append([xc,yc,zc])
					face_triangle[f].append(triangle)

		#for f in self.face_edge.keys():
			#if len(face_triangle[f])>0:
				#print face_triangle[f]
				#print len(face_triangle[f])

		return face_triangle


	def convertVtkJoined(self):
		"""
		fonction pour creer des tas de triangles, avec des cellules  jointives
		"""
		vtkcell_face={}

		#la liste provisoire des triangles, dans l'ancienne numerotation
		triangles_vertex={}
		triangles_normales={}
		#ceci comprendra tout ce qui est vertex -> coordonnees dans la sortie
		vertexMesh_coord={}
		vertex_normale={}
		#la variable k commence e la suite des cles de vertex_coord
		#print k
		#la viariable l sera les clefs des triangles
		l=0
		#ici je boucle sur les cellules et les faces, de telle sorte que je puisse placer les donnees de cellules et faces dans data
		#je remplis vertexMesh_coord, qui est la liste comprenant les vertex des faces ainsi que les centroides des faces
		kv=0
		for cel in self.cell_face.keys():
			if cel in self.liste:
				vertexMesh_coord={}
				triangles_vertex={}
				cellule=vtk.vtkPolyData()
				points=vtk.vtkPoints()
				triangles=vtk.vtkCellArray()
				#c'est ici qu'il faut renumeroter les vertex, afin de dissocier les cellules entre elles. C'est aussi ici que j'applique la correction de localisation en fonction du barycentre de la cellule
				vertex=[]
				for f in self.cell_face[cel]:
					for e in self.face_edge[f]:
						for v in self.edge_vertex[e]:
							vertex.append(v)
				#ici la liste des vertex de la cellule
				vertex=list(set(vertex))
				#vertex_vcel est la traduction entre numerotation des vertex de la cellule et numerotation globale
				vertex_vcel={}
				for v in vertex:
					vertex_vcel[v]=kv
					kv+=1

				for f in self.cell_face[cel]:
					vertex=[]
					x,y,z=0.0,0.0,0.0
					for e in self.face_edge[f]:
						for v in self.edge_vertex[e]:
							vertex.append(v)
					#print vertex
					#on supprime les doublons
					vertex=list(set(vertex))
					#print vertex
					#cette boucle va permettre le calcul de la position du centroide, mais aussi de remplir la liste
					for v in vertex:
						x+=self.vertex_coord[v][0]
						y+=self.vertex_coord[v][1]
						z+=self.vertex_coord[v][2]


						vertexMesh_coord[vertex_vcel[v]]=[self.vertex_coord[v][0],self.vertex_coord[v][1],self.vertex_coord[v][2]]




					if len(vertex)>0:
						x=x/len(vertex)
						y=y/len(vertex)
						z=z/len(vertex)
					else:
						x,y,z=-1,-1,-1

					vertexMesh_coord[kv]=[x,y,z]


					i=0
					for e in self.face_edge[f]:
						triangle=[]
						triangle.append(kv)
						if len(self.edge_vertex[e])==2:
							for c in self.edge_vertex[e]:
								triangle.append(vertex_vcel[c])



						if (len(triangle)==3):
							triangles_vertex[l]=triangle
							vtkcell_face[l]=f
							l+=1
					#incrementer k pour placer les vertex des faces e la fin de la liste
					kv+=1


				for p in vertexMesh_coord.keys():
					points.InsertPoint(p, vertexMesh_coord[p][0], vertexMesh_coord[p][1],vertexMesh_coord[p][2] )

				for t in triangles_vertex.keys():
					if (len(triangles_vertex[t]) == 3):
						triangles.InsertNextCell(3)
						for v in triangles_vertex[t]:
							triangles.InsertCellPoint(v)

				cellule.SetPoints(points)
				cellule.SetStrips(triangles)
				cellule.Update()
				self.cell_vtkTrianglesJoined[cel]=triangles
				self.cell_vtkVertexJoined[cel]=points
				self.cell_vtkPolyDataJoined[cel]=cellule


	def convertVtkSep(self):
		"""
		fonction pour creer des tas de triangles, avec des cellules non jointives
		"""
		vtkcell_face={}

		#la liste provisoire des triangles, dans l'ancienne numerotation

		triangles_normales={}
		#ceci comprendra tout ce qui est vertex -> coordonnees dans la sortie
		vertex_normale={}
		#la variable k commence e la suite des cles de vertex_coord
		#print k
		#la viariable l sera les clefs des triangles
		l=0
		#ici je boucle sur les cellules et les faces, de telle sorte que je puisse placer les donnees de cellules et faces dans data
		#je remplis vertexMesh_coord, qui est la liste comprenant les vertex des faces ainsi que les centroides des faces
		kv=0
		for cel in self.cell_face.keys():
			if cel in self.liste:
				vertexMesh_coord={}
				triangles_vertex={}
				cellule=vtk.vtkPolyData()
				points=vtk.vtkPoints()
				triangles=vtk.vtkCellArray()
				#c'est ici qu'il faut renumeroter les vertex, afin de dissocier les cellules entre elles. C'est aussi ici que j'applique la correction de localisation en fonction du barycentre de la cellule
				vertex=[]
				for f in self.cell_face[cel]:
					for e in self.face_edge[f]:
						for v in self.edge_vertex[e]:
							vertex.append(v)
				#ici la liste des vertex de la cellule
				vertex=list(set(vertex))
				#vertex_vcel est la traduction entre numerotation des vertex de la cellule et numerotation globale
				vertex_vcel={}
				for v in vertex:
					vertex_vcel[v]=kv
					kv+=1

				for f in self.cell_face[cel]:
					vertex=[]
					x,y,z=0.0,0.0,0.0
					for e in self.face_edge[f]:
						for v in self.edge_vertex[e]:
							vertex.append(v)
					#print vertex
					#on supprime les doublons
					vertex=list(set(vertex))
					#print vertex
					#cette boucle va permettre le calcul de la position du centroide, mais aussi de remplir la liste
					for v in vertex:
						x+=self.vertex_coord[v][0]
						y+=self.vertex_coord[v][1]
						z+=self.vertex_coord[v][2]

						dx = self.vertex_coord[v][0] - self.cell_barycentre[cel][0]
						dy = self.vertex_coord[v][1] - self.cell_barycentre[cel][1]
						dz = self.vertex_coord[v][2] - self.cell_barycentre[cel][2]
						norm = sqrt(dx*dx+dy*dy+dz*dz)
						if norm>0.000001:
							dx=dx/norm
							dy=dy/norm
							dz=dz/norm
						else:
							dx,dy,dz=0,0,0

						vertexMesh_coord[vertex_vcel[v]]=[self.vertex_coord[v][0] - dx/4,self.vertex_coord[v][1]  - dy/4,self.vertex_coord[v][2]  - dz/4]




					if len(vertex)>0:
						x=x/len(vertex)
						y=y/len(vertex)
						z=z/len(vertex)
					else:
						x,y,z=-1,-1,-1

					dx = x - self.cell_barycentre[cel][0]
					dy = y - self.cell_barycentre[cel][1]
					dz = z - self.cell_barycentre[cel][2]
					norm = sqrt(dx*dx+dy*dy+dz*dz)
					if norm>0.000001:
						dx=dx/norm
						dy=dy/norm
						dz=dz/norm
					else:
						dx,dy,dz=0,0,0
						print "tissuvirtuel, dx pourri"


					vertexMesh_coord[kv]=[x - dx/4,y  - dy/4,z  - dz/4]


					i=0
					for e in self.face_edge[f]:
						triangle=[]
						triangle.append(kv)
						if len(self.edge_vertex[e])==2:
							for c in self.edge_vertex[e]:
								triangle.append(vertex_vcel[c])



						if (len(triangle)==3):
							triangles_vertex[l]=triangle
							vtkcell_face[l]=f
							l+=1
					#incrementer k pour placer les vertex des faces e la fin de la liste
					kv+=1


				for p in vertexMesh_coord.keys():
					points.InsertPoint(p, vertexMesh_coord[p][0], vertexMesh_coord[p][1],vertexMesh_coord[p][2] )

				for t in triangles_vertex.keys():
					if (len(triangles_vertex[t]) == 3):
						triangles.InsertNextCell(3)
						for v in triangles_vertex[t]:
							triangles.InsertCellPoint(v)

				cellule.SetPoints(points)
				cellule.SetStrips(triangles)
				cellule.Update()
				self.cell_vtkTrianglesSep[cel]=triangles
				self.cell_vtkVertexSep[cel]=points
				self.cell_vtkPolyDataSep[cel]=cellule


	def convertVtk(self):
		"""
		permet de recuperer le nouveau vtk a partir de la liste
		"""
		apJ=vtk.vtkAppendPolyData()
		apS=vtk.vtkAppendPolyData()
		for i in self.liste:
			apJ.AddInput(self.cell_vtkPolyDataJoined[i])
			apS.AddInput(self.cell_vtkPolyDataSep[i])
		apJ.Update()
		apS.Update()
		self.vtkSep.DeepCopy(apS.GetOutput())
		self.vtkJoin.DeepCopy(apJ.GetOutput())
		print "toto"
		#for i in range(self.vtkSep.GetNumberOfCells()):
			#self.vtkcell_cell[i]=int(self.vtkSep.GetCellData().GetArray("identite").GetValue(i))

	def setDataCell(self, dic, nom):
		"""
		mettre les cellules a la couleur d'un facteur quelconque
		"""
		for i in self.liste:
			val=vtk.vtkFloatArray()
			val.SetName(nom)
			if i not in dic.keys():
				print "attention il manque une cellule dans le dictionnaire de valeur, par rapport a la liste"
				for j in range(self.cell_vtkPolyDataJoined[i].GetNumberOfCells()):
					val.InsertValue(j, 0)
			else:
				for j in range(self.cell_vtkPolyDataJoined[i].GetNumberOfCells()):
					val.InsertValue(j, dic[i])
			self.cell_vtkPolyDataSep[i].GetCellData().AddArray(val)
			self.cell_vtkPolyDataSep[i].GetCellData().SetActiveScalars(nom)

			self.cell_vtkPolyDataJoined[i].GetCellData().AddArray(val)
			self.cell_vtkPolyDataJoined[i].GetCellData().SetActiveScalars(nom)


	def createVtkLabels(self):
		"""
		Fonction d'affichage avec vtk et ivtk
		"""
		m=vtkPolyData()
		vertex = vtkPoints()
		provi1=vtkLongArray()

		p=0
		for c in self.liste:
			if c in self.cell_barycentre.keys():
				vertex.InsertPoint(p, self.cell_barycentre[c][0], self.cell_barycentre[c][1],self.cell_barycentre[c][2] )
				provi1.InsertValue(p, c)
				p+=1

		m.SetPoints(vertex)
		m.GetPointData().SetScalars(provi1)
		self.vtkLabels=m


	def createVtkHierarchie(self):
		"""
		cette fonction va creer un sclaire supplementaire qui est la couleur hierarchique
		"""
		pass







	def calcule_normale(self, triangle, cellule):
		"""
		calcule la normale d'un triangle
		"""
		xt, yt, zt = 0.0, 0.0, 0.0
		for v in triangle:
			xt+=v[0]
			yt+=v[1]
			zt+=v[2]

		xt=xt/3.0
		yt=yt/3.0
		zt=zt/3.0

		#ici calcul du vecteur
		dx = xt - self.cell_barycentre[cellule][0]
		dy = yt - self.cell_barycentre[cellule][1]
		dz = zt - self.cell_barycentre[cellule][2]

		norm = sqrt(dx*dx+dy*dy+dz*dz)

		dx=dx/norm
		dy=dy/norm
		dz=dz/norm

		return [dx, dy, dz]

	def calcule_normalePoint(self, point, cellule):
		"""
		calcule la normale d'un vertex d'une cellule
		"""

		#ici calcul du vecteur
		dx = point[0] - self.cell_barycentre[cellule][0]
		dy = point[1] - self.cell_barycentre[cellule][1]
		dz = point[2] - self.cell_barycentre[cellule][2]

		norm = sqrt(dx*dx+dy*dy+dz*dz)

		dx=dx/norm
		dy=dy/norm
		dz=dz/norm

		return [dx, dy, dz]


	def ouvrir2(self, file):
		"""
		pour la sortie txt de romain
		"""
		#initialiser les dictionnaires
		cell_face={}
		cell_barycentre={}
		cell_volume={}
		cell_layer={}
		face_edge={}
		edge_vertex={}
		vertex_coord={}
		#ouvrir le fichier
		fich=open(file,'r')


		debut=[]
		for i in range(15):
			debut.append(fich.readline())
			pass

		i = fich.readline()
		#print "cette ligne : ",i
		i=i.split(':')
		i=i[1].split()

		#print "		bien scindee?", i[3], i[4], i[5]
		vx, vy, vz = float(i[3]), float(i[4]), float(i[5])
		debut.append(fich.readline())

		#ligne1.split(' ')

		#on arrive aux cellules
		#print "		on arrive aux cellules"
		ligne = fich.readline()
		ligne=ligne.split(":")
		#print "			nbcellules a lire = "+ligne[1]
		nbcellules = int(ligne[1])

		for c in range(nbcellules):
			ligne=fich.readline()
			ligne=ligne.split(" ")

		#pour chaque ligne de cellule (for sur le nombre)
		#lire nombre d'elements pour les cellules
		#initialiser le dictionnaire e "i"

			i=int(ligne[0])
			cell_barycentre[i]=[float(ligne[4])*vx,float(ligne[5])*vy,float(ligne[6])*vz]
			cell_volume[i]=float(ligne[2])
			cell_layer[i]=int(ligne[3])
			cell_face[i]=[]

		#on saute une ligne
		fich.readline()
		#on arrive aux faces
		#print "		on arrive aux faces"
		ligne = fich.readline()
		ligne=ligne.split(":")
		#print "			nbfaces a lire = "+ligne[1]
		nbfaces = int(ligne[1])

		for f in range(nbfaces):
			ligne=fich.readline()
			ligne=ligne.split(" ")
		#print node.nodeName, node2.nodeName, cell_barycentre[i]
		#lire nombre d'elements pour les faces
		#pour chaque ligne de face (for sur le nombre)
		#initialiser le dictionnaire i "i"
			i=int(ligne[0])
			cell_face[int(ligne[1])].append(i)
			cell_face[int(ligne[2])].append(i)
			face_edge[i]=[]

		#on saute une ligne
		fich.readline()
		#on arrive aux aretes
		#print "		on arrive aux aretes"
		ligne = fich.readline()
		ligne=ligne.split(":")
		#print "			nbaretes a lire = "+ligne[1]
		nbaretes = int(ligne[1])

		for a in range(nbaretes):
			ligne=fich.readline()
			ligne=ligne.split(":")
		#lire nombre d'elements pour les edges
		#pour chaque ligne de face (for sur le nombre)
		#initialiser le dictionnaire a "i"
			i=int(ligne[0])
			e=ligne[1].split()
			#remplir chaque face decrite avec le edge courant

			for nb in e[1:]:
				face_edge[int(nb)].append(i)

			edge_vertex[i]=[]


		#on saute une ligne
		fich.readline()
		#on arrive aux vertex
		#print "		on arrive aux vertex"
		ligne = fich.readline()
		ligne=ligne.split(":")
		#print "			nbvertex a lire = "+ligne[1]
		nbvertex = int(ligne[1])
		#lire nombre d'elements pour les vertex
		#pour chaque ligne de face (for sur le nombre)
		#initialiser le dictionnaire a "i"
		for v in range(nbvertex):
			ligne=fich.readline()
			l1=ligne.split(":")
			i = int(l1[0])
			coord=l1[1].split()
			vertex_coord[i]=[-1,-1,-1]
			vertex_coord[i][0]=float(coord[0])*vx
			vertex_coord[i][1]=float(coord[1])*vy
			vertex_coord[i][2]=float(coord[2])*vz

			edg=l1[2].split()
			edg=edg[1:]
			for e in edg:
				edge_vertex[int(e)].append(i)


		#fermer le fichier
		fich.close()


		#je rajoute un dictionnaire liant cellule a vertex

		return cell_face, cell_barycentre, cell_volume, cell_layer, face_edge, edge_vertex, vertex_coord, vx, vy, vz





	def distance(self, p1, p2):
		"""
		encore un calcul de distance
		"""
		return sqrt( (p2[0] - p1[0])*(p2[0] - p1[0]) +
				(p2[1] - p1[1])*(p2[1] - p1[1]) +
				(p2[2] - p1[2])*(p2[2] - p1[2]) )


	def extremites(self):
		"""
		calcule les extremites de la structure en terme de barycentre
		"""
		maxX, maxY, maxZ = 0,0,0
		minX, minY, minZ = 100000000, 100000000, 100000000
		for x,y,z in self.cell_barycentre.values():
			if x > maxX:
				maxX=x
			if x < minX:
				minX=x
			if y > maxY:
				maxY=y
			if y < minY:
				minY=y
			if z > maxZ:
				maxZ=z
			if z < minZ:
				minZ=z
		return [minX, minY, minZ],[maxX, maxY, maxZ]



	def definitionListeL1(self, liste):
		"""
		cette fonction renvoie une liste de toutes les cellules sauf le fond
		"""
		l=[]
		for i in self.vertex_coord.values():
			l.append(i[2])
		maximum=max(l)
		minimum=min(l)
		etendue=maximum-minimum

		l=[]
		for c in self.cell_face.keys():
			if (c!=0) and (c!=1) and ((maximum - self.cell_barycentre[c][2]) >(maximum - minimum)/8):
				if (1 in self.cell_cell[c]) and (0 not in self.cell_cell[c]):
					l.append(c)


		l=list(set(l))
		return l


	def definitionListeL2(self, liste):
		"""
		cette fonction renvoie une liste de toutes les cellules sauf le fond
		"""
		l=[]
		for c in self.cell_face.keys():
			if (self.cell_layer[c]!=0) and (self.cell_layer[c]!=1):
				for c1 in self.cell_cell[c]:
					if (1 not in self.cell_cell[c]) and (0 not in self.cell_cell[c]):
						l.append(c)
		l=list(set(l))
		return l


	def definitionListe1(self, liste=[]):
		"""
		cette fonction renvoie une liste de toutes les cellules sauf le fond
		"""
		l=[]
		for c in self.cell_cell.keys():
			l.append(c)
		return l

	def definitionListe4(self, liste):
		"""
		cette fonction renvoie une liste de toutes les cellules sauf le fond
		"""
		l=[]
		for c in self.cell_face.keys():
			if self.distance(self.cell_barycentre[c],[liste[0]*self.vx,liste[1]*self.vy,liste[2]*self.vz]) > liste[3] and self.cell_layer[c]!=0:
				l.append(c)
			else:
				pass

		return l


	def definitionListe2(self, liste):
		"""
		cette fonction renvoie les cellules dont le barycentre est dans la sphere precisee
		"""
		l=[]
		for c in self.cell_face.keys():
			if self.distance(self.cell_barycentre[c],[liste[0]*self.vx,liste[1]*self.vy,liste[2]*self.vz]) < liste[3] and self.cell_layer[c]!=0:
				l.append(c)
			else:
				pass

		return l

	def definitionListe3(self, liste):
		"""
		cette fonction renvoie les cellules precisees en entree
		"""
		return liste


	def doMenuFileExit(self):
		sys.exit( 0 )


	def getCellCell(self,c):
		return self.cell_cell[c]

	def getCellFace(self,c):
		return self.cell_face[c]

	def sauver(self, nomFichier, type):
		"""fonction de sauvegarde"""
		f=vtk.vtkPolyDataWriter()
		f.SetFileName(nomFichier)
		if type==1:
			f.SetInput(self.vtkSep)
		if type==2:
			f.SetInput(self.vtkJoin)
		if (type!=1) and (type!=2):
			print "vous n'avez pas defini la bonne structure a sauver (sauver de tissuVirtuel)"
		f.Write()
		del f


	def marqueur(self, fichier, nom):
		"""
		permet de chopper un fichier de marqueur et de recuperer les valeurs dans le dictionnaire de marqueur.
		"""
		dico={}
		try:
			f=open(fichier)
		except IOError:
			print "fichier de marqueur inexistant"
			return

		#on se debarasse des deux premieres lignes
		f.readline()
		f.readline()

		for l in f:
			l=l.split()
			if len(l)>2:
				dico[int(l[1].split(",")[0])+1]=float(l[-1])

		f.close()
		self.cell_marqueur[nom]=dico



def main():
	args = sys.argv[1:]
	print "WELCOME TO CUSTOM VTK CREATOR, PLEASE FOLLOW INSTRUCTIONS"
	if len(args)==0:
		print tissuVirtuel.__doc__
	else:
		tissu = tissuVirtuel(infile)

	print "THANK YOU FOR YOUR VISIT ;)"


if __name__ == '__main__':
    main()






#poubelle



	#def ouvrir3(self, rootNode, level):
		#celNbFilles={}
		#celFilles={}

		#for node in rootNode.childNodes:
			#if node.nodeType==Node.ELEMENT_NODE:
				#for attr in node.attributes.keys():
					##print node.attributes.get(attr).nodeName
					#if node.attributes.get(attr).nodeName=="id":
						##print node.attributes.get(attr).nodeName, node.attributes.get(attr).nodeValue
						#id = int(node.attributes.get(attr).nodeValue)
					#if node.attributes.get(attr).nodeName=="nb_filles":
						#b = int(node.attributes.get(attr).nodeValue)
						##print node.attributes.get(attr).nodeName, node.attributes.get(attr).nodeValue

				#c=[]

				#for node2 in node.childNodes:
					#if node2.nodeType==Node.ELEMENT_NODE:
						#for attr in node2.attributes.keys():
							##print node2.attributes.get(attr).nodeName
							#if node2.attributes.get(attr).nodeName == "id":
								##print node2.attributes.get(attr).nodeValue
								#c.append(int(node2.attributes.get(attr).nodeValue))

				#celNbFilles[id]=b
				#celFilles[id]=c
		#return celNbFilles, celFilles


	#def calculLien(self):
		#celLien={}
		#for c in self.celCoord1.keys():
			#if self.celNbFilles[c]!=0:
				#Xtot, Ytot, Ztot = [],[],[]
				#for cf in self.celFilles[c]:
					#Xtot.append(self.celCoord2[cf][0])
					#Ytot.append(self.celCoord2[cf][1])
					#Ztot.append(self.celCoord2[cf][2])
				#Xmoy,Ymoy,Zmoy=sum(Xtot)/float(self.celNbFilles[c]), sum(Ytot)/float(self.celNbFilles[c]), sum(Ztot)/float(self.celNbFilles[c])
				#celLien[c]=Xmoy-self.celCoord1[c][0], Ymoy-self.celCoord1[c][1],Zmoy-self.celCoord1[c][2]
			#else:
				#celLien[c]=[0,0,0]
		#return celLien

