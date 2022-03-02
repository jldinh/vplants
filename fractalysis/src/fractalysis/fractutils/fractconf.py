#! /usr/bin/env python
"""
:Authors:
  - Da SILVA David
:Organization: Virtual Plants
:Contact: david.da_silva:cirad.fr
:Version: 1.0
:Date: July 2005
"""

import os


class pathDB:
    """
    :Abstract: Contains and deals with all working directories within *fractalysis* project.
    """

    def __init__(self):
        """
        Initialize all needed directories according that they already exist in the *fractalysis* project.

        The directories are :
          - HOMEPROJECT : the path to the *fractalysis* project
          - SCRIPTDIR : the patrh to the scripts directory
          - PLANTDBDIR : the path to the plant database directory (ie. containing the *.ipl* files, see `infoPlant`)
          - SCENEDIR : the path to the plant's scene directory
          - MTGDIR : the path to the MTG directory
          - MSTDIR : the path to the MST directory
          - RESULTDIR : the general result directory
          - PYRESULTDIR : the python result directory
          - SOURCEDIR : the sources directory
          - LIGHTRESULTDIR : the light interception result directory
        """
        #dirname = os.getcwd()
        dirname = '/home/ddasilva/dev/fractalysis'
        dirs=dirname.split(os.sep)

        try:
            idx=dirs.index('fractalysis')
        except ValueError:
            print "This module should be called inside fractalysis/ project"

        hpjt = '/'
        for i in range(idx+1):
            hpjt = os.path.join(hpjt, dirs[i])
        
        self.HOMEPROJECT = hpjt

        tmp =  os.path.join(self.HOMEPROJECT ,'Scripts')
        if os.path.isdir(tmp):
            self.SCRIPTDIR = tmp

        tmp = os.path.join(self.HOMEPROJECT, 'PlantDB')
        if os.path.isdir(tmp):
            self.PLANTDBDIR = tmp

        tmp = os.path.join(self.PLANTDBDIR,'scenes')
        if os.path.isdir(tmp):
            self.SCENEDIR = tmp

        tmp = os.path.join(self.HOMEPROJECT,'src')
        if os.path.isdir(tmp):
            self.SOURCEDIR = tmp

        tmp = os.path.join(self.PLANTDBDIR,'MTG')
        if os.path.isdir(tmp):
            self.MTGDIR = tmp

        tmp = os.path.join(self.PLANTDBDIR,'mst')
        if os.path.isdir(tmp):
            self.MSTDIR = tmp
            
        tmp =  os.path.join(self.HOMEPROJECT, 'Results')
        if os.path.isdir(tmp):
            self.RESULTDIR = tmp

        tmp = os.path.join(self.RESULTDIR, 'PythonOutput')
        if os.path.isdir(tmp):
            self.PYRESULTDIR = tmp
        
        tmp = os.path.join(self.RESULTDIR, 'light')
        if os.path.isdir(tmp):
            self.LIGHTRESULTDIR = tmp
        
    def getDir(self, dir):
        """
        :param dir: The name of the wanted directory. See `__init__` for valid name. 
        
        :Returns: The absolute path to the wanted directory
        :Returntype: absolute path
        """
        try:
            return eval('self.%s' % dir)
        except AttributeError:
            return None

    def cout(self):
        """
        Print on the current display (screen) all embeded directories.
        """
        print "HomeProject path HOMEPROJECT : ", self.HOMEPROJECT
        print "Scripts path SCRIPTDIR : ",self.SCRIPTDIR
        print "PlantDB path PLANTDBDIR : ", self.PLANTDBDIR
        print "Scenes path SCENEDIR : ", self.SCENEDIR
        print "Mtg path MTGDIR : ", self.MTGDIR
        print "Mst path MSTDIR : ", self.MSTDIR
        print "Results path RESULTDIR : ", self.RESULTDIR
        print "Sources path SOURCEDIR : ", self.SOURCEDIR
        print "Python output path PYRESULTDIR : ", self.PYRESULTDIR
        print "Light interception output path LIGHTRESULTDIR : ", self.LIGHTRESULTDIR
        
