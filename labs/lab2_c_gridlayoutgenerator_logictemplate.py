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

def generate_inv_template(laygen, cellname, instance_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin,
                 routing_grid_m2m3_pin, origin=np.array([0,0]), phantom_layer=None):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    # cell generation
    mycell = cellname
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)  # select the cell to work on

    # placement
    in0 = laygen.place(instance_pfix+'N0', 'nmos4_fast_boundary', pg, xy=origin)
    in1 = laygen.relplace(instance_pfix+'N1', 'nmos4_fast_center_nf1_left', pg, in0.name)
    in2 = laygen.relplace(instance_pfix+'N2', 'nmos4_fast_boundary', pg, in1.name)
    ip0 = laygen.relplace(instance_pfix+'P0', 'pmos4_fast_boundary', pg, in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(instance_pfix+'P1', 'pmos4_fast_center_nf1_left', pg, ip0.name, transform='MX')
    ip2 = laygen.relplace(instance_pfix+'P3', 'pmos4_fast_boundary', pg, ip1.name, transform='MX')

    # route
    # input
    laygen.route(None, metal[1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.route(None, metal[2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    ri0 = laygen.route(None, metal[3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=ip1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G0', gridname=rg_m1m2)
    laygen.via(None, np.array([-1, 0]), refinstname=ip1.name, refpinname='G0', gridname=rg_m2m3)
    # output
    laygen.route(None, metal[2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstname1=in1.name, refpinname1='D0')
    laygen.route(None, metal[2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0', refinstname1=ip1.name, refpinname1='D0')
    ro0 = laygen.route(None, metal[3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstname1=ip1.name, refpinname1='D0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', gridname=rg_m2m3)
    # power and groud rail
    xy = laygen.get_template_size(in2.cellname, rg_m1m2) * np.array([1, 0])
    laygen.route('RVDD0', metal[2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip2.name)
    laygen.route('RVSS0', metal[2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)
    # power and ground route
    xy_s0 = laygen.get_template_pin_coord(in1.cellname, 'S0', rg_m1m2)[0, :]
    laygen.route(None, metal[1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='S0', refinstname1=in1.name)
    laygen.route(None, metal[1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='S0', refinstname1=ip1.name)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2)

    # pin
    laygen.pin_from_rect(name='I', layer=pin[1], rect=ri0, gridname=rg_m1m2_pin)
    laygen.pin_from_rect(name='O', layer=pin[3], rect=ro0, gridname=rg_m2m3_pin)

    # add template
    laygen.add_template_from_cell()

def generate_tinv_template(laygen, cellname, instance_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin,
                 routing_grid_m2m3_pin, origin=np.array([0,0]), phantom_layer=None):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    # cell generation
    mycell = cellname
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)  # select the cell to work on

    # placement
    in0 = laygen.place(instance_pfix+'N0', 'nmos4_fast_boundary', pg, xy=origin)
    in1 = laygen.relplace(instance_pfix+'N1', 'nmos4_fast_center_nf1_left', pg, in0.name)
    in2 = laygen.relplace(instance_pfix+'N2', 'nmos4_fast_center_nf1_right', pg, in1.name)
    in3 = laygen.relplace(instance_pfix+'N3', 'nmos4_fast_boundary', pg, in2.name)
    ip0 = laygen.relplace(instance_pfix+'P0', 'pmos4_fast_boundary', pg, in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(instance_pfix+'P1', 'pmos4_fast_center_nf1_left', pg, ip0.name, transform='MX')
    ip2 = laygen.relplace(instance_pfix+'P2', 'pmos4_fast_center_nf1_right', pg, ip1.name, transform='MX')
    ip3 = laygen.relplace(instance_pfix+'P3', 'pmos4_fast_boundary', pg, ip2.name, transform='MX')

    # route
    # input
    laygen.route(None, metal[1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.route(None, metal[2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    ri0 = laygen.route(None, metal[3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m1m2)
    laygen.via(None, np.array([-1, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # en
    laygen.route(None, metal[2], xy0=np.array([0, 0]), xy1=np.array([2, 0]), gridname0=rg_m1m2,
                 refinstname0=in2.name, refpinname0='G0', refinstname1=in2.name, refpinname1='G0')
    ren0 = laygen.route(None, metal[3], xy0=np.array([1, 0]), xy1=np.array([1, 2]), gridname0=rg_m2m3,
                         refinstname0=in2.name, refpinname0='G0', refinstname1=in2.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in2.name, refpinname='G0', gridname=rg_m1m2)
    laygen.via(None, np.array([1, 0]), refinstname=in2.name, refpinname='G0', gridname=rg_m2m3)
    # enb
    laygen.route(None, metal[2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip2.name, refpinname0='G0', refinstname1=ip2.name, refpinname1='G0')
    renb0 = laygen.route(None, metal[3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                         refinstname0=ip2.name, refpinname0='G0', refinstname1=ip2.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='G0', gridname=rg_m1m2)
    laygen.via(None, np.array([-1, 0]), refinstname=ip2.name, refpinname='G0', gridname=rg_m2m3)
    # output
    laygen.route(None, metal[2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in2.name, refpinname0='D0', refinstname1=in2.name, refpinname1='D0')
    laygen.route(None, metal[2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=ip2.name, refpinname0='D0', refinstname1=ip2.name, refpinname1='D0')
    ro0 = laygen.route(None, metal[3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in2.name, refpinname0='D0', refinstname1=ip2.name, refpinname1='D0')
    laygen.via(None, np.array([0, 0]), refinstname=in2.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in2.name, refpinname='D0', gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='D0', gridname=rg_m2m3)
    # power and groud rail
    xy = laygen.get_template_size(in3.cellname, rg_m1m2) * np.array([1, 0])
    laygen.route('RVDD0', metal[2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip3.name)
    laygen.route('RVSS0', metal[2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in3.name)
    # power and ground route
    xy_s0 = laygen.get_template_pin_coord(in1.cellname, 'S0', rg_m1m2)[0, :]
    laygen.route(None, metal[1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='S0', refinstname1=in1.name)
    laygen.route(None, metal[1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='S0', refinstname1=ip1.name)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2)
    #print(renb0.display())
    # pin
    laygen.pin_from_rect(name='I', layer=pin[3], rect=ri0, gridname=rg_m2m3_pin)
    laygen.pin_from_rect(name='EN', layer=pin[3], rect=ren0, gridname=rg_m2m3_pin)
    laygen.pin_from_rect(name='ENB', layer=pin[3], rect=renb0, gridname=rg_m2m3_pin)
    laygen.pin_from_rect(name='O', layer=pin[3], rect=ro0, gridname=rg_m2m3_pin)

    # add template
    laygen.add_template_from_cell()

def generate_space_template(laygen, cellname, instance_pfix, placement_grid, origin=np.array([0,0]),phantom_layer=None):
    pg = placement_grid

    # cell generation
    mycell = cellname
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)  # select the cell to work on

    # placement
    in0 = laygen.place(instance_pfix+'N0', 'nmos4_fast_space', pg, xy=origin)
    ip0 = laygen.relplace(instance_pfix+'P0', 'pmos4_fast_space', pg, in0.name, direction='top', transform='MX')

    # power and groud rail
    xy = laygen.get_template_size(in0.cellname, rg_m1m2) * np.array([1, 0])
    laygen.route('RVDD0', metal[2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route('RVSS0', metal[2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # add template
    laygen.add_template_from_cell()

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

laygen = laygo.GridLayoutGenerator(physical_res=res)
laygen.layers['metal'] = metal
laygen.layers['pin'] = pin
laygen.layers['prbnd'] = prbnd
if tech=='laygo10n': #fake technology
    laygen.use_phantom = True

utemplib = tech+'_microtemplates_dense'
laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
laygen.templates.sel_library(utemplib)
laygen.grids.sel_library(utemplib)
#laygen.templates.display()
#laygen.grids.display()

#library generation
workinglib = tech+'_templates_logic'

laygen.add_library(workinglib)
laygen.sel_library(workinglib)

#grid
pg = 'placement_basic' #placement grid
rg_m1m2 = 'route_M1_M2_mos'
rg_m2m3 = 'route_M2_M3_mos'
rg_m1m2_pin = 'route_M1_M2_basic'
rg_m2m3_pin = 'route_M2_M3_basic'

phantom_layer=None
generate_inv_template(laygen, 'inv_1x', instance_pfix='IINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
             routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin)

generate_tinv_template(laygen, 'tinv_1x', instance_pfix='ITINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
             routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin)

generate_space_template(laygen, 'space_1x', instance_pfix='ISPACE0', placement_grid=pg)

laygen.display()

#display
#laygen.display()
#laygen.templates.display()
laygen.save_template(filename=tech+'_templates_logic_templates.yaml', libname=workinglib)

#bag export, if bag does not exist, gds export
mycell_list=['inv_1x', 'tinv_1x', 'space_1x']
import imp
try:
    imp.find_module('bag')
    import bag
    prj = bag.BagProject()
    for mycell in mycell_list:
        laygen.sel_cell(mycell)
        laygen.export_BAG(prj, array_delimiter=['[', ']'])
except ImportError:
    laygen.export_GDS('output.gds', cellname=mycell_list, layermapfile=tech+".layermap")  # change layermapfile
