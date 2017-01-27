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

"""Lab1-a: generate layout on physical grid
    Instructions
    1. For BAG export, copy this file to BAG working directory and uncomment BAG portions
    2. For GDS export, make sure laygo is visible in the working folder and prepare the layermap file of given
       technology (usually be found in the technology lib folder)
    3. modify metal and mpin list for given technology
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import laygo
import numpy as np
import yaml
#import logging;logging.basicConfig(level=logging.DEBUG)

import os.path
if os.path.isfile("laygo_config.yaml"):
    with open("laygo_config.yaml", 'r') as stream:
        techdict = yaml.load(stream)
        tech = techdict['tech_lib']
        metal = techdict['metal_layers']
        pin = techdict['pin_layers']
        text = techdict['text_layer']
        prbnd = techdict['prboundary_layer']
        res = techdict['physical_resolution']
else:
    print("no config file exists. loading default settings")
    tech = "freePDK45"
    metal = [['metal0', 'donotuse'],
             ['metal1', 'drawing'],
             ['metal2', 'drawing'],
             ['metal3', 'drawing'],
             ['metal4', 'drawing'],
             ['metal5', 'drawing']]
    pin = [['text', 'drawing'],
           ['metal1', 'pin'],
           ['metal2', 'pin'],
           ['metal3', 'pin'],
           ['metal4', 'pin'],
           ['metal5', 'pin']]
    text = ['text', 'drawing']
    prbnd = ['prBoundary', 'drawing']
    res=0.0025

#working library name
workinglib = 'laygo_working'

laygen = laygo.BaseLayoutGenerator(res=res) #res should be your minimum grid resolution
laygen.add_library(workinglib)
laygen.sel_library(workinglib)

#generation layout elements
mycell = '_generate_example_1'
laygen.add_cell(mycell)
laygen.sel_cell(mycell)
laygen.add_rect(None, np.array([[0, 0], [1.0, 0.1]]), metal[1])
laygen.add_rect(None, np.array([[[0, 0], [0.1, 1.0]], [[1.0, 0], [1.1, 1]]]), metal[2])
mycell2 = '_generate_example_2'
laygen.add_cell(mycell2)
laygen.sel_cell(mycell2)
laygen.add_inst(None, workinglib, mycell, xy=np.array([2, 0]), shape=np.array([1, 1]),
                spacing=np.array([1, 1]), transform='R0')
laygen.add_inst(None, workinglib, mycell, xy=np.array([0, 2]), shape=np.array([2, 3]),
                spacing=np.array([1, 2]), transform='R0')
laygen.add_text(None, 'text0', np.array([1, 1]), text)

laygen.display()

#bag export, if bag does not exist, gds export
import imp
try:
    imp.find_module('bag')
    #bag export
    print("export to BAG")
    import bag
    prj = bag.BagProject()
    laygen.sel_cell(mycell)
    laygen.export_BAG(prj, array_delimiter=['[', ']'])
    laygen.sel_cell(mycell2)
    laygen.export_BAG(prj, array_delimiter=['[', ']'])
except ImportError:
    #gds export
    print("export to GDS")
    laygen.sel_cell(mycell) #cell selection
    laygen.export_GDS('lab1_generated.gds', layermapfile=tech+".layermap") #change layermapfile
    laygen.sel_cell(mycell2)
    laygen.export_GDS('lab1_generated2.gds', cellname=[mycell, mycell2], layermapfile=tech+".layermap")