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

laygen = laygo.GridLayoutGenerator(physical_res=res)
laygen.layers['metal'] = metal
laygen.layers['pin'] = pin
laygen.layers['prbnd'] = prbnd
if tech=='laygo10n': #fake technology
    laygen.use_phantom = True

laygen.add_library(workinglib)
laygen.sel_library(workinglib)

laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
laygen.templates.sel_library(utemplib)
laygen.grids.sel_library(utemplib)
#laygen.templates.display()
#laygen.grids.display()

mycell = '_generate_example_3'
pg = 'placement_basic' #placement grid
laygen.add_cell(mycell)
laygen.sel_cell(mycell) #select the cell to work on

in0=laygen.place(None, 'nmos4_fast_left', pg, xy=np.array([0,0]))
#placement on grid
laygen.place(None, 'nmos4_fast_boundary', pg, xy=np.array([2,0]))
laygen.place(None, 'nmos4_fast_center_nf2', pg, xy=np.array([3,0]))
in1=laygen.place(None, 'nmos4_fast_center_nf2', pg, xy=np.array([5,0]))
#abutted placement on grid
in2=laygen.relplace(None, 'nmos4_fast_center_nf1_right', pg, in1.name)
in3=laygen.relplace(None, 'nmos4_fast_boundary', pg, in2.name)
in4=laygen.relplace(None, 'nmos4_fast_tap', pg, in3.name)
in5=laygen.relplace(None, 'nmos4_fast_right', pg, in4.name)
ip0=laygen.relplace(None, 'pmos4_fast_left', pg, in0.name, direction='top', transform='MX')
ip1=laygen.relplace(None, 'pmos4_fast_boundary', pg, ip0.name, transform='MX')
ip2=laygen.relplace(None, 'pmos4_fast_center_nf2', pg, ip1.name, transform='MX')
ip3=laygen.relplace(None, 'pmos4_fast_center_nf2', pg, ip2.name, transform='MX')
ip4=laygen.relplace(None, 'pmos4_fast_center_nf1_right', pg, ip3.name, transform='MX')
ip5=laygen.relplace(None, 'pmos4_fast_boundary', pg, ip4.name, transform='MX')
ip6=laygen.relplace(None, 'pmos4_fast_tap', pg, ip5.name, transform='MX')
ip7=laygen.relplace(None, 'pmos4_fast_right', pg, ip6.name, transform='MX')

#route on grid
laygen.route(None, metal[2], xy0=np.array([4,3]), xy1=np.array([6,3]), gridname0='route_M1_M2_mos')
#route on grid with reference objects
laygen.route(None, metal[2], xy0=np.array([1,3]), xy1=np.array([2,3]), gridname0='route_M1_M2_mos',
             refinstname0=ip1.name, transform0='MX', refinstname1=ip1.name, transform1='MX')
#route on grid, pin reference
laygen.route(None, metal[1], xy0=np.array([0,0]), xy1=np.array([0,0]), gridname0='route_M1_M2_mos',
             refinstname0=in1.name, refpinname0='G0', refinstname1=ip3.name, refpinname1='G0')

#via placement on grid
laygen.via(None, np.array([4,3]), gridname='route_M1_M2_mos')
#via placement on grid with offset
laygen.via(None, np.array([1,3]), gridname='route_M1_M2_mos', offset=np.array([0.45, 0.96]), transform='MX')
#via placement on grid with pin reference
laygen.via(None, np.array([0,0]), refinstname=ip3.name, refpinname='G0', gridname='route_M1_M2_mos')

laygen.display()

#bag export, if bag does not exist, gds export
import imp
try:
    imp.find_module('bag')
    import bag
    prj = bag.BagProject()
    laygen.sel_cell(mycell)
    laygen.export_BAG(prj, array_delimiter=['[', ']'])
except ImportError:
    laygen.sel_cell(mycell)  # cell selection
    laygen.export_GDS('output.gds', layermapfile=tech+".layermap")  # change layermapfile