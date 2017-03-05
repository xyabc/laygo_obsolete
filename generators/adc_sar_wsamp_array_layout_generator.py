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

"""ADC library
"""
import laygo
import numpy as np
#from logic_layout_generator import *
from math import log
from copy import deepcopy
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_sar_wsamp_array(laygen, objectname_pfix, workinglib, sar_name, 
                       placement_grid,
                       routing_grid_m3m4, routing_grid_m4m5, routing_grid_m5m6, routing_grid_m5m6_thick,
                       routing_grid_m5m6_basic_thick,
                       num_bits=9, num_slices=8, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick

    # placement
    # sar
    isar=laygen.place(name="I" + objectname_pfix + 'SLICE0', templatename=sar_name,
                      gridname=pg, xy=origin, shape=np.array([num_slices, 1]), template_libname=workinglib)

    #reference coordinates
    pdict_m3m4 = [] 
    pdict_m4m5 = []
    pdict_m5m6 = []
    pdict_m5m6_thick = []
    pdict_m5m6_thick_basic = []
    for i in range(num_slices):
        pdict_m3m4.append(laygen.get_inst_pin_coord(None, None, rg_m3m4, index=np.array([i, 0])))
        pdict_m4m5.append(laygen.get_inst_pin_coord(None, None, rg_m4m5, index=np.array([i, 0])))
        pdict_m5m6.append(laygen.get_inst_pin_coord(None, None, rg_m5m6, index=np.array([i, 0])))
        pdict_m5m6_thick.append(laygen.get_inst_pin_coord(None, None, rg_m5m6_thick, index=np.array([i, 0])))
        pdict_m5m6_thick_basic.append(laygen.get_inst_pin_coord(None, None, rg_m5m6_basic_thick, index=np.array([i, 0])))
    #vref route
    for i in range(num_slices):
        rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6], 
                                 xy0=pdict_m5m6_thick_basic[i][isar.name]['VREF_M5L<0>'][0], 
                                 xy1=np.array([0, pdict_m5m6_thick_basic[i][isar.name]['VREF_M5L<0>'][0][1]+i]), 
                                 gridname=rg_m5m6_basic_thick)
        laygen.create_boundary_pin_form_rect(rh, rg_m5m6_basic_thick, 'VREF' + str(i) + '<0>', laygen.layers['pin'][6], size=8, direction='left')
        rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6], 
                                 xy0=pdict_m5m6_thick_basic[i][isar.name]['VREF_M5L<1>'][0], 
                                 xy1=np.array([0, pdict_m5m6_thick_basic[i][isar.name]['VREF_M5L<1>'][0][1]+i+num_slices]), 
                                 gridname=rg_m5m6_basic_thick)
        laygen.create_boundary_pin_form_rect(rh, rg_m5m6_basic_thick, 'VREF' + str(i) + '<1>', laygen.layers['pin'][6], size=8, direction='left')
        rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6], 
                                 xy0=pdict_m5m6_thick_basic[i][isar.name]['VREF_M5L<2>'][0], 
                                 xy1=np.array([0, pdict_m5m6_thick_basic[i][isar.name]['VREF_M5L<2>'][0][1]+i+2*num_slices]), 
                                 gridname=rg_m5m6_basic_thick)
        laygen.create_boundary_pin_form_rect(rh, rg_m5m6_basic_thick, 'VREF' + str(i) + '<2>', laygen.layers['pin'][6], size=8, direction='left')
        rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6], 
                                 xy0=pdict_m5m6_thick_basic[i][isar.name]['VREF_M5R<0>'][0], 
                                 xy1=np.array([0, pdict_m5m6_thick_basic[i][isar.name]['VREF_M5R<0>'][0][1]+i]), 
                                 gridname=rg_m5m6_basic_thick)
        rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6], 
                                 xy0=pdict_m5m6_thick_basic[i][isar.name]['VREF_M5R<1>'][0], 
                                 xy1=np.array([0, pdict_m5m6_thick_basic[i][isar.name]['VREF_M5R<1>'][0][1]+i+num_slices]), 
                                 gridname=rg_m5m6_basic_thick)
        rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6], 
                                 xy0=pdict_m5m6_thick_basic[i][isar.name]['VREF_M5R<2>'][0], 
                                 xy1=np.array([0, pdict_m5m6_thick_basic[i][isar.name]['VREF_M5R<2>'][0][1]+i+2*num_slices]), 
                                 gridname=rg_m5m6_basic_thick)
    #ofp/ofm route
    for i in range(num_slices):
        rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][3], layerh=laygen.layers['metal'][4], 
                                 xy0=pdict_m3m4[i][isar.name]['OSP'][0], 
                                 xy1=np.array([0, pdict_m3m4[i][isar.name]['OSP'][0][1]-(num_slices*3)+3*i]), 
                                 gridname=rg_m3m4)
        laygen.create_boundary_pin_form_rect(rh, rg_m3m4, 'OSP' + str(i), laygen.layers['pin'][4], size=8, direction='left')
        rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][3], layerh=laygen.layers['metal'][4], 
                                 xy0=pdict_m3m4[i][isar.name]['OSM'][0], 
                                 xy1=np.array([0, pdict_m3m4[i][isar.name]['OSM'][0][1]-(num_slices*3)+3*i+1]), 
                                 gridname=rg_m3m4)
        laygen.create_boundary_pin_form_rect(rh, rg_m3m4, 'OSM' + str(i), laygen.layers['pin'][4], size=8, direction='left')
    #pins
    sar_template = laygen.templates.get_template(sar_name, workinglib)
    sar_pins=sar_template.pins
    sar_xy=deepcopy(isar.xy[0])
    for i in range(num_slices):
        pin_prefix_list=['INP', 'INM', 'CLK', 'CLKO', 'EXTCLK', 'EXTSEL_CLK']
        for pfix in pin_prefix_list:
            pn=pfix + str(i)
            laygen.add_pin(pn, pn, sar_xy+sar_pins[pfix]['xy'], sar_pins[pfix]['layer'])
        laygen.add_pin('ASCLKD' + str(i) + '<0>', 'ASCLKD' + str(i) + '<0>', sar_xy+sar_pins['CKDSEL0<0>']['xy'], sar_pins['CKDSEL0<0>']['layer'])
        laygen.add_pin('ASCLKD' + str(i) + '<1>', 'ASCLKD' + str(i) + '<1>', sar_xy+sar_pins['CKDSEL0<1>']['xy'], sar_pins['CKDSEL0<1>']['layer'])
        laygen.add_pin('ASCLKD' + str(i) + '<2>', 'ASCLKD' + str(i) + '<2>', sar_xy+sar_pins['CKDSEL1<0>']['xy'], sar_pins['CKDSEL1<0>']['layer'])
        laygen.add_pin('ASCLKD' + str(i) + '<3>', 'ASCLKD' + str(i) + '<3>', sar_xy+sar_pins['CKDSEL1<1>']['xy'], sar_pins['CKDSEL1<1>']['layer'])
        for j in range(num_bits):
            laygen.add_pin('ADCOUT' + str(i) + '<'+str(j)+'>', 'ADCOUT' + str(i) + '<'+str(j)+'>', sar_xy+sar_pins['ADCOUT<'+str(j)+'>']['xy'], sar_pins['ADCOUT<'+str(j)+'>']['layer'])
        sar_xy+=sar_template.xy[1]*np.array([1, 0])
    #VDD/VSS pins (just duplicate from lower hierarchy cells)
    sar_xy=deepcopy(isar.xy[0])
    vddcnt=0
    vsscnt=0
    for pn, p in sar_pins.items():
        if pn.startswith('VDD'):
            if sar_pins[pn]['xy'][0][0]==0 and sar_pins[pn]['xy'][1][0]==sar_template.xy[1][0]: #check if it's horizontal rail
                pxy=sar_xy+sar_pins[pn]['xy']
                pxy[1][0]=pxy[1][0]*num_slices
                laygen.add_pin('VDD' + str(vddcnt), 'VDD', pxy, sar_pins[pn]['layer'])
                vddcnt+=1
        if pn.startswith('VSS'):
            if sar_pins[pn]['xy'][0][0]==0 and sar_pins[pn]['xy'][1][0]==sar_template.xy[1][0]: #check if it's horizontal rail
                pxy=sar_xy+sar_pins[pn]['xy']
                pxy[1][0]=pxy[1][0]*num_slices
                laygen.add_pin('VSS' + str(vsscnt), 'VSS', pxy, sar_pins[pn]['layer'])
                vsscnt+=1
    ''' 
    for p in pdict_m5m6[0][isar.name]:
        if p.startswith('VDD'):
            xy0=np.vstack((pdict_m5m6_thick[0][isar.name][p][0], pdict_m5m6_thick[-1][isar.name][p][1]))
            laygen.pin(name='VDD' + str(vddcnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VDD')
            vddcnt+=1
        if p.startswith('VSS'):
            xy0=np.vstack((pdict_m5m6_thick[0][isar.name][p][0], pdict_m5m6_thick[-1][isar.name][p][1]))
            laygen.pin(name='VSS' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VSS')
            vsscnt+=1
    '''

if __name__ == '__main__':
    laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")

    import imp
    try:
        imp.find_module('bag')
        laygen.use_phantom = False
    except ImportError:
        laygen.use_phantom = True

    tech=laygen.tech
    utemplib = tech+'_microtemplates_dense'
    logictemplib = tech+'_logic_templates'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    #library load or generation
    workinglib = 'adc_sar_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib+'.yaml'): #generated layout file exists
        laygen.load_template(filename=workinglib+'.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m1m2_thick = 'route_M1_M2_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=9
    num_slices=9
    #load from preset
    load_from_file=True
    yamlfile_system_input="adc_sar_dsn_system_input.yaml"
    if load_from_file==True:
        with open(yamlfile_system_input, 'r') as stream:
            sysdict_i = yaml.load(stream)
        num_bits=sysdict_i['n_bit']
        num_slices=sysdict_i['n_interleave']
    #sar generation
    cellname='sar_wsamp_'+str(num_bits)+'b_array_'+str(num_slices)+'slice'
    sar_name = 'sar_wsamp_'+str(num_bits)+'b'

    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sar_wsamp_array(laygen, objectname_pfix='SA0', workinglib=workinglib, sar_name=sar_name,
                             placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m5m6=rg_m5m6,
                             routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick,
                             num_bits=num_bits, num_slices=num_slices, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    

    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)
    #bag export, if bag does not exist, gds export
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
