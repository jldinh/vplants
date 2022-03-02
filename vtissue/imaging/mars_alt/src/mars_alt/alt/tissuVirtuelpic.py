# -*- python -*-
#
#       vplants.mars_alt.alt.tissuVirtuelpic
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

#modification labo
#13 avril 2011 :
#fusion version maison - labo

import sys, string
import math
from math import *
import Tkinter
import vtk
import tkFont
import tissuVirtuel
import os
from numpy import isnan
from numpy.random import random
import copy

#from aide import *

class tissuVirtuelpic(tissuVirtuel.tissuVirtuel):
	"""
		conversion de .pic en tissu
	"""
	def __init__(self,fich="",vtk1="toto.vtk",param="4",liste=[]):
		#~ tissuVirtuel.tissuVirtuel.__init__(self,fich,vtk1,param,liste)
		#~ print "mere initialisee"
		self.nom=fich
		#les dictionnaires sont initialises ici
		try:
			self.ouvrir2(fich)
		except:
			print "l'ouverture a rate"
			sys.exit(0)
		print "fichier ouvert"
		print "entree dans cell_vtk"
		self.cell_vtk=self.creeVtkFromCells()
		self.vtkVec=vtk.vtkPolyData()
		self.vtkTens=vtk.vtkPolyData()
		self.vtkBary=vtk.vtkPolyData()
		print "dictionnaire cell_vtk termine"

		self.addScalarsDefault()
		self.addTensorsDefault()
		self.addVectorsDefault()
		print "scalaires par defaut places dans les vtk"
		self.vtkSep=vtk.vtkPolyData()
		self.vtkJoin=vtk.vtkPolyData()
		self.convertVtkJoined=self.convertVtkSep=self.convertVtk
		self.convertVtk()
		print "vtk final cree"



	def ouvrir2(self, fich):
		"""
		ouvre un fichier pic en considerant que "fich" contient toutes les infos necessaires

		coordonnees, cell_bary, cell_volume, cell_cell, cell_cellS, cell_cellP, liste
		"""
		import cPickle
		import gzip
		f=gzip.open(fich+".pic"+"z","rb")
		dico=cPickle.load(f)
		f.close()

		self.dico=dico
		self.cell_coords=dico["cell_coords"]
		self.cell_cell = dico["cell_cell"]
		self.cell_cellP=dico["cell_cellP"]
		self.liste = dico["liste"]
		self.header=dico["header"]

		#~ print self.liste

		#ici gestion de version des picz
		###d'abord gestion de l'identite
		if ("identite" not in self.dico.keys()) and ("scalaire_identite" not in self.dico.keys()):
			self.dico["scalaire_identite"]={}
			d=self.dico["scalaire_identite"]
			for i in self.cell_coords.keys():
				d[i]=i


		if "identite" in self.dico.keys():
			self.dico["scalaire_identite"]=self.dico["identite"]
			del self.dico["identite"]

		if "cell_barycentre" in self.dico.keys():
			self.dico["vecteur_cell_barycentre"]=self.dico["cell_barycentre"]
			self.cell_barycentre=self.dico["vecteur_cell_barycentre"]
			del self.dico["cell_barycentre"]

		###puis du volume
		if "cell_volume" in self.dico.keys():
			self.dico["scalaire_cell_volume"]=self.dico["cell_volume"]
			self.cell_volume=self.dico["scalaire_cell_volume"]
			del self.dico["cell_volume"]

		if "scalaire_cell_volume" in self.dico.keys():
			self.cell_volume=self.dico["scalaire_cell_volume"]

		###puis de la l1
		if "l1" not in self.dico:
			self.l1=[c for c in self.liste if c in self.cell_cell.get(1,[])]
		else:
			self.l1=self.dico["l1"]

		###puis de la liste des constantes
		if "listeValeurs" not in dico.keys():
			self.dico["listeValeurs"]=[k for k in self.dico.keys() if k not in ["cell_coords","cell_cell","cell_cellP","liste","header"]]


		self.cell_layer={}
		for i in self.liste:
			self.cell_layer[i]=0



	def creeVtkFromCells(self):
		"""
		permet de recuperer le nouveau vtk a partir de la liste
		"""
		cell_vtkPolyData={}
		cellule={}
		points={}
		resultat={}
		g={}
		val={}
		val2={}
		l=self.cell_coords.keys()
		cell_coords=self.cell_coords
		l.remove(0)
		l.remove(1)
		for c in l:
			cellule=vtk.vtkPolyData()
			points=vtk.vtkPoints()
			#on insere les points en utilisant toutes les coordonnees
			for p in cell_coords[c]:
				points.InsertNextPoint(p[0], p[1], p[2] )
			#on cree le polydata dans lequel on met les points
			cellule.SetPoints(points)
			#on cree les scalaires de base

			#~ print cellule[c].GetNumberOfPoints()
			#on va tenter de faire des trucs subtils, genre creer un mesh
			g=vtk.vtkVertexGlyphFilter()
			g.SetInput(cellule)
			toto=vtk.vtkPolyData()
			g.SetOutput(toto)
			inter=g.GetOutput()
			resultat=inter
			resultat.Update()
			#~ resultat[c].GetCellData().SetActiveScalars("volume")
			#enfin on remplit le dictionnaire avec le polydata tout chaud
			cell_vtkPolyData[c]=resultat
			#~ toto.ReleaseData()
			#~ print resultat[c].GetNumberOfCells()
		return cell_vtkPolyData

	def addScalarsDefault(self):
		"""
		fonction choppant le dictionnaire de cellules et creant les scalaires correspondant a la liste
		de dictionnaires donnee en string
		"""
		#d'abord on ne garde que les donnees qui sont des scalaires
		listeS=[]
		for i in self.dico.keys():
			if i[:8]=="scalaire":
				listeS.append(i[9:])

		for cvtk in self.cell_vtk.keys():
			for l in listeS:
				val=vtk.vtkFloatArray()
				val.SetName(l)
				if cvtk in self.dico["scalaire_"+l].keys():
					v=self.dico["scalaire_"+l][cvtk]
				else:
					v=0
				for j in range(self.cell_vtk[cvtk].GetNumberOfCells()):
					val.InsertValue(j, v)
				self.cell_vtk[cvtk].GetCellData().AddArray(val)


	def addScalarsDefaultBary(self):
		"""
		fonction choppant le dictionnaire de cellules et creant les scalaires correspondant a la liste
		de dictionnaires donnee en string
		"""
		#d'abord on ne garde que les donnees qui sont des scalaires
		listeS=[]
		for i in self.dico.keys():
			if i[:8]=="scalaire":
				listeS.append(i[9:])

		p=vtk.vtkPoints()
		ordo=self.dico["vecteur_cell_barycentre"].keys()
		ordo.sort()
		for cvtk in ordo:
			if not isnan(self.dico["vecteur_cell_barycentre"][cvtk][0]):
				x=self.dico["vecteur_cell_barycentre"][cvtk]
				p.InsertNextPoint(x[0],x[1],x[2])
				self.vtkBary.SetPoints(p)
		for l in listeS:
			val=vtk.vtkFloatArray()
			val.SetNumberOfComponents(3)
			val.SetName(l)
			for cvtk in ordo:
				if not isnan(self.dico["vecteur_cell_barycentre"][cvtk][0]):
					if cvtk in self.dico["scalaire_"+l].keys():
						x=self.dico["scalaire_"+l][cvtk]
					else:
						x=0
					val.InsertNextValue(x)
			self.vtkBary.GetPointData().AddArray(val)

	def addVectorsDefault(self):
		"""
		fonction choppant le dictionnaire de cellules et creant les vecteurs correspondant a la liste
		de dictionnaires donnee en string
		"""
		listeS=[]
		for i in self.dico.keys():
			if i[:7]=="vecteur":
				listeS.append(i[8:])
		#d'abord faire les points d'ancrage au niveau des barycentres
		p=vtk.vtkPoints()
		for cvtk in self.liste:
			if not isnan(self.dico["vecteur_cell_barycentre"][cvtk][0]):
				x=self.dico["vecteur_cell_barycentre"][cvtk]
				p.InsertNextPoint(x[0],x[1],x[2])
				self.vtkVec.SetPoints(p)
		for l in listeS:
			val=vtk.vtkFloatArray()
			val.SetNumberOfComponents(3)
			val.SetName(l)
			for cvtk in self.liste:
				if not isnan(self.dico["vecteur_cell_barycentre"][cvtk][0]):
					if cvtk in self.dico["vecteur_"+l].keys():
						x=self.dico["vecteur_"+l][cvtk]
					else:
						x=[0,0,0]
					val.InsertNextTuple3(x[0],x[1],x[2])
			self.vtkVec.GetPointData().AddArray(val)

	def addTensorsDefault(self):
		"""
		fonction choppant le dictionnaire de cellules et creant les tenseurs correspondant a la liste
		de dictionnaires donnee en string
		"""
		#premierement on teste si les donnees sont bien des tenseurs :
		listeS=[]
		for i in self.dico.keys():
			if i[:7]=="tenseur":
				listeS.append(i[8:])
		#d'abord faire les points d'ancrage au niveau des barycentres
		p=vtk.vtkPoints()
		for cvtk in self.liste:
			if not isnan(self.dico["vecteur_cell_barycentre"][cvtk][0]):
				x=self.dico["vecteur_cell_barycentre"][cvtk]
				p.InsertNextPoint(x[0],x[1],x[2])
				self.vtkTens.SetPoints(p)
		for l in listeS:
			val=vtk.vtkFloatArray()
			val.SetNumberOfComponents(9)
			val.SetName(l)
			for cvtk in self.liste:
				if not isnan(self.dico["vecteur_cell_barycentre"][cvtk][0]):
					if cvtk in self.dico["tenseur_"+l].keys():
						x=self.dico["tenseur_"+l][cvtk]
					else:
						x=[[0,0,0],[0,0,0],[0,0,0]]
					val.InsertNextTuple9(x[0][0],x[0][1],x[0][2], x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])
			self.vtkTens.GetPointData().AddArray(val)






	def convertVtk(self):
		"""
		cree le vtk final en utilisant append
		"""
		#append est un element vtk qui agglomere plusieurs polydata
		ap=vtk.vtkAppendPolyData()
		poly=self.cell_vtk
		#la liste est censee contenir les cellules du tissu sous forme d'entiers
		#poly est un dictionnaire [int]-[vtkPolyData]
		for i in self.liste:
			if i in poly.keys():
				ap.AddInput(poly[i])
			else:
				print "attention, vous avez essaye de mettre une cellule inexistante dans appendPolydata"
				print "vous êtes dans la fonction convertVtk de tissuVirtuelpic"

		#ici on s'assure que les arrays de donnees presents dans les vtkPolyData de chaque cellule
		#soient donnes a append
		cellule=self.cell_vtk[self.liste[-1]]
		for k in range(cellule.GetCellData().GetNumberOfArrays()):
			name=cellule.GetCellData().GetArrayName(k)
			ap.SetInputArrayToProcess(0,0,0,k,name)
		#ici indispensable pour bien faire en sorte que le pipe vtk soit active
		ap.Update()
		#ici je fait sep et join pour des raisons de compatibilite avec les fonctionnalites de vis
		self.vtkSep.DeepCopy(ap.GetOutput())
		self.vtkJoin=self.vtkSep

	def createVtkLabels(self, dico={}):
		"""
		Fonction d'affichage avec vtk et ivtk
		"""
		m=vtk.vtkPolyData()
		vertex = vtk.vtkPoints()
		provi1=vtk.vtkLongArray()

		p=0
		for c in self.liste:
			if c in dico.keys():
				vertex.InsertPoint(p, self.cell_barycentre[c][0], self.cell_barycentre[c][1],self.cell_barycentre[c][2] )
				provi1.InsertValue(p, dico[c])
				p+=1

		m.SetPoints(vertex)
		m.GetPointData().SetScalars(provi1)
		self.vtkLabels=m

	def test_affichage(self):
		"""
		petit test avec ivtk
		"""
		import enthought.tvtk.tools.ivtk as ivtk
		v=ivtk.viewer()

		a=vtk.vtkLODActor()
		m=vtk.vtkPolyDataMapper()
		m.SetInput(self.vtkSep)
		a.SetMapper(m)
		m.SetScalarRange(0,len(self.liste))
		m.ScalarVisibilityOn()
		lut = vtk.vtkLookupTable()
		m.SetLookupTable(lut)
		lut.SetNumberOfColors(2000)
		for i in range(2000):
			lut.SetTableValue(i,random(),random(),random(),1)
		a.GetProperty().SetPointSize(5.)
		v.scene.add_actor(a)


	def test_affichage_bary(self):
		"""
		petit test avec ivtk
		"""
		import enthought.tvtk.tools.ivtk as ivtk
		v=ivtk.viewer()

		a=vtk.vtkLODActor()
		m=vtk.vtkPolyDataMapper()
		m.SetInput(self.vtkTens)
		a.SetMapper(m)
		m.SetScalarRange(0,len(self.liste))
		m.ScalarVisibilityOn()
		lut = vtk.vtkLookupTable()
		m.SetLookupTable(lut)
		lut.SetNumberOfColors(2000)
		for i in range(2000):
			lut.SetTableValue(i,random(),random(),random(),1)
		a.GetProperty().SetPointSize(5.)
		v.scene.add_actor(a)


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
		self.dico["scalaire_"+nom]=dico

def main():
	args = sys.argv[1:]
	print "WELCOME TO TISSUVIRTUELPIC, let's convert your picz into nice vtk files"
	if len(args)==0:
		print tissuVirtuel.__doc__
	else:
		tissu = tissuVirtuelpic(args[0])
		w=vtk.vtkPolyDataWriter()
		w.SetFileName(tissu.nom+"_cellules"+".vtk")
		w.SetInput(tissu.vtkSep)
		w.Update()
		w.SetFileName(tissu.nom+"_Tenseurs"+".vtk")
		w.SetInput(tissu.vtkTens)
		w.Update()


	print "THANK YOU FOR YOUR VISIT ;)"


if __name__ == '__main__':
    main()
