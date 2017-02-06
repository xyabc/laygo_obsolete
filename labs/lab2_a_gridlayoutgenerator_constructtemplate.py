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

"""Lab1: generate layout on physical grid
   1. Copy this file to working directory
   2. For GDS export, prepare layermap file
"""
import laygo
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
        print(tech + " loaded sucessfully")
else:
    print("no config file exists. loading default settings")
    tech = "freePDK45"
    metal = [['metal0', 'donotuse'],
             ['metal1', 'drawing'],
             ['metal2', 'drawing'],
             ['metal3', 'drawing'],
             ['metal4', 'drawing'],
             ['metal5', 'drawing'],
             ['metal6', 'drawing'],
             ['metal7', 'drawing'],
             ['metal8', 'drawing'],
             ['metal9', 'drawing'],
             ]
    pin = [['text', 'drawing'],
           ['metal1', 'pin'],
           ['metal2', 'pin'],
           ['metal3', 'pin'],
           ['metal4', 'pin'],
           ['metal5', 'pin'],
           ['metal6', 'pin'],
           ['metal7', 'pin'],
           ['metal8', 'pin'],
           ['metal9', 'pin'],
           ]
    text = ['text', 'drawing']
    prbnd = ['prBoundary', 'drawing']
    res=0.0025

workinglib = 'laygo_working'
utemplib = tech+'_microtemplates_dense'

laygen = laygo.GridLayoutGenerator(physical_res=res) #change physical grid resolution
laygen.layers['metal'] = metal
laygen.layers['pin'] = pin
laygen.layers['prbnd'] = prbnd
if tech=='laygo10n': #fake technology
    laygen.use_phantom = True

laygen.add_library(workinglib)
laygen.sel_library(workinglib)

#bag import, if bag does not exist, gds import
import imp
try:
    imp.find_module('bag')
    #bag import
    print("import from BAG")
    import bag
    prj = bag.BagProject()
    db=laygen.import_BAG(prj, utemplib, append=False)
except ImportError:
    #gds import
    print("import from GDS")
    db = laygen.import_GDS(tech+'_microtemplates_dense.gds', layermapfile=tech+".layermap", append=False)

#construct template
laygen.construct_template_and_grid(db, utemplib, layer_boundary=prbnd)

#display and save
laygen.templates.display()
laygen.grids.display()
laygen.templates.export_yaml(filename=tech+'_microtemplates_dense_templates.yaml')
laygen.grids.export_yaml(filename=tech+'_microtemplates_dense_grids.yaml')



