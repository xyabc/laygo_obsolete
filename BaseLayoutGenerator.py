#!/usr/bin/python
########################################################################################################################
#
# Copyright (c) 2014, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################################################################

'''Base Layout Generator'''
__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

from . import LayoutIO
from .LayoutDB import *
from .LayoutObject import * 
import numpy as np
#import LayoutIO
#from LayoutDB import *
#from LayoutObject import *


class BaseLayoutGenerator():
    """Base layout generator class

    BaseLayoutGenerator is handling layout objects on physical grids
    """
    db = LayoutDB() # Layout database
    annotate_layer = ['text', 'drawing']  # annotate_layer
    annotate_height = 0.01

    #physical resolution
    @property
    def res(self): return self.db.res
    
    @res.setter
    def res(self, value): self.db.res=value


    def __init__(self, res=0.005):
        """
        Constructor


        """
        self.db=LayoutDB(res=res)

    # aux functions
    def display(self, libname=None, cellname=None):
        """
        Display DB information

        Parameters
        ----------
        libname : library name
        cellname : cell name
        """
        self.db.display(libname, cellname)

    # library and cell related functions
    def add_library(self, name):
        """
        Add a library to the design dictionary

        Parameters
        ----------
        name : str
            library name
        """
        self.db.add_library(name)

    def add_cell(self, name, libname=None):
        """
        Add a cell to the specified library

        Parameters
        ----------
        name : str
            cellname
        libname :
            library name (if None, self.plib is used)
        """
        self.db.add_cell(name, libname)

    def sel_library(self, libname):
        """
        Select a library to work on

        Parameters
        ----------
        libname : str
            library name
        """
        self.db.sel_library(libname)

    def sel_cell(self, cellname):
        """
        Select a cell to work on

        Parameters
        ----------
        cellname : str
            cellname
        """
        self.db.sel_cell(cellname)

    # geometry related functions
    def add_rect(self, name, xy, layer, netname=None):
        """
        Add a rect to selected cell

        Parameters
        ----------
        name : str
            rect name
        xy : [float, float]
            xy coordinate
        layer : [layername, purpose]
            layer name an purpose


        Returns
        -------
        rect object
        """
        return self.db.add_rect(name, xy, layer, netname)

    def add_pin(self, name, netname, xy, layer):
        """
        Add a pin to selected cell

        Parameters
        ----------
        name : str
            pin object name
        netname : str
            net name
        xy : [float, float]
            xy coordinate
        layer : [layername, purpose]
            layer name an purpose


        Returns
        -------
        pin object
        """
        return self.db.add_pin(name, netname, xy, layer)

    def add_text(self, name, text, xy, layer):
        """
        Add a pin to selected cell

        Parameters
        ----------
        name : str
            pin object name
        text : str
            text string
        xy : [float, float]
            xy coordinate
        layer : [layername, purpose]
            layer name an purpose


        Returns
        -------
        text object
        """
        return self.db.add_text(name, text, xy, layer)

    def add_inst(self, name, libname, cellname, xy=None, shape=np.array([1, 1]), spacing=np.array([0, 0]),
                 transform='R0'):
        """
        Add an instance to the specified library and cell (_plib, _pstr)

        Parameters
        ----------
        name : str
            instance name
        libname : str
            cell library name (not output library)
        cellname : str
            cellname
        xy : [float, float]
            xy coordinate
        shape : np.array([x0, y0])
            array shape parameter
        spacing : np.array([x0, y0])
            array spacing parameter
        transform : str
            transform parameter

        Returns
        -------
        instance object
        """
        return self.db.add_inst(name, libname, cellname, xy, shape, spacing, transform)

    # access functions
    def get_rect(self, name, libname=None):
        """
        Get rect object
        Parameters
        ----------
        name :
        libname : str
         libname. if None, self.db._plib is used
        """
        return self.db.get_rect(name, libname)

    def get_inst(self, name=None, libname=None):
        """
        Get instance object
        Parameters
        ----------
        name : str
         instance name, if none, all instance is returned
        libname : str
         libname. if None, self.db._plib is used
        """
        return self.db.get_inst(name, libname)

    def get_pin(self, name, libname=None):
        """
        Get pin object
        Parameters
        ----------
        name :
        libname : str
         libname. if None, self.db._plib is used
        """
        return self.db.get_pin(name, libname)

    # db I/O functions
    def export_GDS(self, filename, libname=None, cellname=None, layermapfile="default.layermap", physical_unit=1e-9,
                   logical_unit=0.001, pin_label_height=0.1, text_height=0.1):
        """
        Export specified cell(s) to a GDS file

        Parameters
        ----------
        filename : str
            output filename
        layermapfile : str
            layermap filename
            example) default.layermap
                #technology layer information
                #layername layerpurpose stream# datatype
                text        drawing 100 0
                prBoundary  drawing 101 0
                metal1      drawing 50  0
                metal1      pin     50  10
                metal2      drawing 51  0
                metal2      pin     51  10
        physical_unit :
        logical_unit :
        pin_label_height : pin label height
        text_height : text height
        """
        if libname==None: libname=self.db.plib
        if cellname==None: cellname=self.db.pcell
        if pin_label_height==None:
            pin_label_height=self.annotate_height
        if text_height==None:
            text_height==self.annotate_height
        LayoutIO.export_GDS(self.db, libname, cellname, filename=filename, layermapfile=layermapfile,
                            physical_unit=physical_unit, logical_unit=logical_unit, pin_label_height=pin_label_height,
                            text_height=text_height)

    def export_BAG(self, prj, array_delimiter=['[',']'], via_tech='cdsDefTechLib'):
        """
        Export specified cell(s) to BagProject object

        Parameters
        ----------
        db : LayoutDB
            Layout db object
        libname : str
            name of library to be exported
        cellname : list or str
            name of cells to be exported
        prj : BagProject
            bag object to export
        array_delimiter : list or str
            array delimiter for multiple placements
        via_tech : str
            via technology entry for BagProject. Not being used currently because instances are used for via connections
        """
        LayoutIO.export_BAG(self.db,self.db._plib,self.db._pcell,prj,array_delimiter=array_delimiter, via_tech=via_tech)

    def import_GDS(self, filename, layermapfile="default.layermap", instance_libname=None, physical_unit=1e-9,
                   logical_unit=0.001, append=True):
        """
        Import layout database from gds file

        Parameters
        ----------
        filename : gds filename
        layermapfile : layermap filename
        instance_libname : library name of instantiated structure
        physical_unit :
        logical_unit :

        Returns
        -------

        """
        db=LayoutIO.import_GDS(filename=filename, layermapfile=layermapfile, instance_libname=instance_libname,
                               physical_unit=physical_unit, logical_unit=logical_unit, res=self.db._res)
        if append==True:
            self.db.merge(db)
        return db

    def import_BAG(self, prj, libname, cellname=None, yamlfile="import_BAG_scratch.yaml", append=True):
        """
        Import layout database from BagProject object

        Parameters
        ----------
        prj : BagProject
            bag object to export
        libname : str
            name of library to be exported
        cellname : list or str
            name of cells to be exported
        yamlfile : str
            scratch yaml file path

        Returns
        -------

        """
        db=LayoutIO.import_BAG(prj=prj, libname=libname, cellname=cellname, yamlfile=yamlfile, res=self.db._res)
        if append==True:
            self.db.merge(db)
        return db

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    workinglib = 'laygo_working'
    utemplib = 'laygo_microTemplates'

    metal=[['metal0', 'donotuse'],
           ['metal1', 'drawing'],
           ['metal2', 'drawing'],
           ['metal3', 'drawing'],
           ['metal4', 'drawing'],
           ['metal5', 'drawing']]
    mpin=[['text', 'drawing'],
          ['metal1', 'pin'],
          ['metal2', 'pin'],
          ['metal3', 'pin'],
          ['metal4', 'pin'],
          ['metal5', 'pin']]
    text=['text', 'drawing']

    laygen = BaseLayoutGenerator()
    laygen.set_res(0.005)
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)

    # layout
    mycell = '_placement_example_1'
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    laygen.add_rect(None, np.array([[0, 0], [0.1, 0.01]]), metal[1])
    laygen.add_rect(None, np.array([[[0, 0], [0.01, 0.1]], [[0.1, 0], [0.11, 0.1]]]), metal[2])
    mycell2 = '_placement_example_2'
    laygen.add_cell(mycell2)
    laygen.sel_cell(mycell2)
    laygen.add_inst(None, workinglib, mycell, xy=np.array([0.2, 0.2]), shape=np.array([0, 0]),
                    spacing=np.array([0, 0]), transform='R0')
    laygen.add_inst(None, workinglib, mycell, xy=np.array([0, 0.2]), shape=np.array([2, 3]),
                    spacing=np.array([0.1, 0.2]), transform='R0')
    laygen.add_inst(None, workinglib, mycell, xy=np.array([[0.8, 0], [0.8, 0.4]]), shape=np.array([0, 0]),
                    spacing=np.array([0.1, 0.2]), transform='R0')
    laygen.add_pin(None, netname='net0', xy=np.array([[0, 0], [0.01, 0.01]]), layer=mpin[1])
    laygen.add_text(None, 'text0', np.array([0.1, 0.1]), text)

    # display
    laygen.display()
