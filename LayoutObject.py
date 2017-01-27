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

'''Layout Object Class'''
__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import numpy as np
import logging

class LayoutObject():
    """Layout object class"""
    name = None  # Object name
    xy = np.array([0, 0]) # Cooridinate

    def __init__(self, name, res, xy):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.ndarray
            coordinates array
        """
        self.name = name
        self.res = res
        self.xy = self.trim(xy)

    #Aux functions
    def trim(self, x):
        """
        Trim coordinate numbers to grid resolution

        Parameters
        ----------
        x : np.ndarray or float
            number of list to be trimmed

        Returns
        -------
        x : np.ndarray or float
            trimmed cooridnates

        """
        return np.round(x / self.res) * self.res

    def display(self):
        """Display object information"""
        print("  " + self.name + " xy:" +str(np.around(self.xy, decimals=10).tolist()))


class Rect(LayoutObject):
    """Rect object class"""
    layer=None
    xy=None
    netname=None

    @property
    def height(self): return abs(self.xy[0][1]-self.xy[1][1])

    @property
    def width(self): return abs(self.xy[0][0]-self.xy[1][0])

    @property
    def size(self): return np.hstack((self.width, self.height))

    @property
    def cx(self): return 0.5*(self.xy[0][0]+self.xy[1][0])

    @property
    def cy(self): return 0.5*(self.xy[0][1]+self.xy[1][1])

    @property
    def center(self): return np.hstack((self.cx, self.cy))

    def __init__(self, name, res, xy, layer, netname):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.array([[x0, y0], [x1, y1]])
            xy coorinates
        layer : [layer, pupose]
            layer name and purpose
        netname : str
            net name
        """
        self.layer = layer
        self.netname=netname
        #bx1, bx2 = sorted(xy[:,0].tolist()) #need to be changed..
        #by1, by2 = sorted(xy[:,1].tolist())
        #ll = np.array([bx1, by1])  # lower-left
        #ur = np.array([bx2, by2])  # upper-right
        #xy=np.vstack([ll,ur])
        LayoutObject.__init__(self, name, res, xy)

    def display(self):
        """Display object information"""
        print("  [Rect]" + self.name + " layer:" + str(self.layer) +
              " xy:" + str(np.around(self.xy, decimals=10).tolist()) +
              " center:" + str(np.around(self.center, decimals=10).tolist()) +
              " size:" + str(np.around(self.size, decimals=10).tolist()))


class Pin(LayoutObject):
    """Pin object class"""
    layer=None
    xy=None
    netname=None

    def __init__(self, name, res, xy, netname, layer):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.array([[x0, y0], [x1, y1]])
            xy coorinates
        netname : str
            net name
        layer : [layer, pupose]
            layer name and purpose
        """
        self.netname = netname
        self.layer = layer
        LayoutObject.__init__(self, name, res, xy)

    def display(self):
        """Display object information"""
        print("  [Pin]" + self.name + " layer:" + str(self.layer) + " xy:" + str(self.xy.tolist()))


class Text(LayoutObject):
    """Text object class"""
    layer=None
    xy=None
    text=None

    def __init__(self, name, res, xy, layer, text):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.array([[x0, y0], [x1, y1]])
            xy coorinates
        layer : [layer, pupose]
            layer name and purpose
        text : str
            text entry
        """
        self.layer = layer
        self.text = text
        LayoutObject.__init__(self, name, res, xy)

    def display(self):
        """Display object information"""
        print("  [Text]" + self.name + " text:" + self.text +
              " layer:" + str(self.layer) + " xy:" + str(np.around(self.xy, decimals=10).tolist()))


class Instance(LayoutObject):
    """Instance object class"""
    libname=None
    cellname=None
    num_row=0
    num_col=0
    sp_row=0
    sp_col=0
    transform='R0'

    def __init__(self, name, res, xy, libname, cellname, shape=np.array([1, 1]), spacing=np.array([0, 0]), transform='R0'):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.array([[x0, y0], [x1, y1], ...])
            xy coordinates
        libname : str
            library name
        cellname : str
            cell name
        shape : np.array([col, row])
            array size
        spacing : np.array([xspacing, yspacing])
            spacing between array elements
        transform : str
            transformal parameter
        """
        LayoutObject.__init__(self, name, res, xy)
        self.libname = libname
        self.cellname = cellname
        self.shape = shape
        self.spacing = self.trim(spacing)
        self.transform = transform

    def display(self):
        """Display object information"""
        print("  [Instance]" + self.name + " libname:" + self.libname +  " cellname:" + self.cellname +
              " xy:" + str(self.xy.tolist()) + " shape:" + str(self.shape.tolist()) +
              " spacing:" + str(self.spacing.tolist()) + " transform:" + str(self.transform))


