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
from math import log
import yaml
import os
import laygo.GridLayoutGeneratorHelper as laygenhelper #utility functions
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_tisaradc_body(laygen, objectname_pfix, libname, tisar_core_name, tisar_space_name, 
                           placement_grid,
                           routing_grid_m3m4, routing_grid_m4m5, routing_grid_m5m6, routing_grid_m5m6_thick, 
                           routing_grid_m5m6_thick_basic, routing_grid_m6m7_thick, 
                           num_bits=9, num_slices=8, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    rg_m6m7_thick = routing_grid_m6m7_thick

    # placement
    ispace0 = laygen.place(name="I" + objectname_pfix + 'SP0', templatename=tisar_space_name,
                      gridname=pg, xy=origin, template_libname=libname)
    space_template = laygen.templates.get_template(tisar_space_name, libname)
    space_pins=space_template.pins
    space0_xy=ispace0.xy[0]
    sar_origin = laygen.get_template_size(ispace0.cellname, gridname=pg, libname=workinglib)*np.array([1, 0])
    isar = laygen.place(name="I" + objectname_pfix + 'SAR0', templatename=tisar_core_name,
                      gridname=pg, xy=sar_origin, template_libname=libname)
    sar_template = laygen.templates.get_template(tisar_core_name, libname)
    sar_pins=sar_template.pins
    sar_xy=isar.xy[0]
    space_origin = sar_origin + laygen.get_template_size(isar.cellname, gridname=pg, libname=workinglib)*np.array([1, 0])
    #ispace0 = laygen.relplace(name="I" + objectname_pfix + 'SP0', templatename=tisar_space_name,
    #                  gridname=pg, refinstname=isar.name, template_libname=libname)
    ispace1 = laygen.place(name="I" + objectname_pfix + 'SP1', templatename=tisar_space_name,
                      gridname=pg, xy=space_origin, template_libname=libname)
    space1_xy=ispace1.xy[0]

    #prboundary
    sar_size = laygen.templates.get_template(tisar_core_name, libname=libname).size
    space_size = laygen.templates.get_template(tisar_space_name, libname=libname).size

    #VDD/VSS pins (just duplicate from lower hierarchy cells)
    vddcnt=0
    vsscnt=0
    for pn, p in space_pins.items():
        if pn.startswith('VDD'):
            #pxy=np.array([space0_xy+space_pins[pn]['xy'][0], space1_xy+space_pins[pn]['xy'][1]])
            pxy=np.array([[0, space0_xy[1]+space_pins[pn]['xy'][0][1]], 
                          [space_size[0]*2+sar_size[0], space1_xy[1]+space_pins[pn]['xy'][1][1]]])
            laygen.add_pin('VDD' + str(vddcnt), 'VDD', pxy, laygen.layers['pin'][6])
            laygen.add_rect(None, pxy, laygen.layers['metal'][6])
            vddcnt+=1
        if pn.startswith('VSS'):
            #pxy=np.array([space0_xy+space_pins[pn]['xy'][0], space1_xy+space_pins[pn]['xy'][1]])
            pxy=np.array([[0, space0_xy[1]+space_pins[pn]['xy'][0][1]], 
                          [space_size[0]*2+sar_size[0], space1_xy[1]+space_pins[pn]['xy'][1][1]]])
            laygen.add_pin('VSS' + str(vsscnt), 'VSS', pxy, laygen.layers['pin'][6])
            laygen.add_rect(None, pxy, laygen.layers['metal'][6])
            vsscnt+=1
    
    #other pins - duplicate
    pin_prefix_list=['INP', 'INM', 'OSP', 'OSM', 'VREF', 'ASCLKD', 'EXTCLK', 'EXTSEL_CLK', 'ADCOUT']
    for pn, p in sar_pins.items():
        for pfix in pin_prefix_list:
            if pn.startswith(pfix):
                laygen.add_pin(pn, sar_pins[pn]['netname'], sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
    '''
    #input pins
    for i in range(num_input_track):
        rinp.append(laygen.route(None, laygen.layers['metal'][6], xy0=np.array([in_x0, in_y1+2*i]), xy1=np.array([in_x1, in_y1+2*i]), gridname0=rg_m5m6_thick_temp_sig))
        rinm.append(laygen.route(None, laygen.layers['metal'][6], xy0=np.array([in_x0, in_y1+2*i+1]), xy1=np.array([in_x1, in_y1+2*i+1]), gridname0=rg_m5m6_thick_temp_sig))

    #retimer output pins
    for i in range(num_slices):
        for j in range(num_bits):
            pn='out_'+str(i)+'<'+str(j)+'>'
            pn_out='ADCOUT'+str(i)+'<'+str(j)+'>'
            xy=pdict_m3m4[iret.name][pn]
            xy[0][1]=0
            r=laygen.route(None, layer=laygen.layers['metal'][3], xy0=xy[0], xy1=xy[1], gridname0=rg_m3m4)
            laygen.create_boundary_pin_form_rect(r, rg_m3m4, pn_out, laygen.layers['pin'][3], size=4, direction='bottom')
    #extclk pins
    for i in range(num_slices):
            pn='EXTCLK'+str(i)
            pn_out='EXTCLK'+str(i)
            xy=pdict_m5m6[isar.name][pn]
            xy[0][1]=0
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=xy[0], xy1=xy[1], gridname0=rg_m5m6)
            laygen.create_boundary_pin_form_rect(r, rg_m5m6, pn_out, laygen.layers['pin'][5], size=4, direction='bottom')
    #extclk_sel pins
    for i in range(num_slices):
            pn='EXTSEL_CLK'+str(i)
            pn_out='EXTSEL_CLK'+str(i)
            xy=pdict_m5m6[isar.name][pn]
            xy[0][1]=0
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=xy[0], xy1=xy[1], gridname0=rg_m5m6)
            laygen.create_boundary_pin_form_rect(r, rg_m5m6, pn_out, laygen.layers['pin'][5], size=4, direction='bottom')
    #asclkd pins
    for i in range(num_slices):
        for j in range(4):
            pn='ASCLKD'+str(i)+'<'+str(j)+'>'
            pn_out='ASCLKD'+str(i)+'<'+str(j)+'>'
            xy=pdict_m5m6[isar.name][pn]
            xy[0][1]=0 
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=xy[0], xy1=xy[1], gridname0=rg_m5m6)
            laygen.create_boundary_pin_form_rect(r, rg_m5m6, pn_out, laygen.layers['pin'][5], size=4, direction='bottom')
    #osp/osm pins
    for i in range(num_slices):
        laygen.pin(name='OSP' + str(i), layer=laygen.layers['pin'][4], xy=pdict_m4m5[isar.name]['OSP' + str(i)], gridname=rg_m4m5)
        laygen.pin(name='OSM' + str(i), layer=laygen.layers['pin'][4], xy=pdict_m4m5[isar.name]['OSM' + str(i)], gridname=rg_m4m5)
    #vref pins
    for i in range(num_slices):
        laygen.pin(name='VREF' + str(i) + '<0>', layer=laygen.layers['pin'][6], xy=pdict_m5m6_thick_basic[isar.name]['VREF' + str(i) + '<0>'], gridname=rg_m5m6_thick_basic)
        laygen.pin(name='VREF' + str(i) + '<1>', layer=laygen.layers['pin'][6], xy=pdict_m5m6_thick_basic[isar.name]['VREF' + str(i) + '<1>'], gridname=rg_m5m6_thick_basic)
        laygen.pin(name='VREF' + str(i) + '<2>', layer=laygen.layers['pin'][6], xy=pdict_m5m6_thick_basic[isar.name]['VREF' + str(i) + '<2>'], gridname=rg_m5m6_thick_basic)
    #sar-retimer routes (data)
    for i in range(num_slices):
        for j in range(num_bits):
            laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4], 
                            xy0=pdict_m4m5[isar.name]['ADCOUT'+str(i)+'<'+str(j)+'>'][0], 
                            xy1=pdict_m3m4[iret.name]['in_'+str(i)+'<'+str(j)+'>'][0], 
                            track_y=pdict_m4m5[isar.name]['ADCOUT'+str(i)+'<'+str(j)+'>'][0][1]+j*2+2, 
                            gridname=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4, extendl=0, extendr=0)
    #sar-retimer routes (clock)
    rg_m3m4_temp_clk='route_M3_M4_basic_temp_clk'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m3m4, gridname_output=rg_m3m4_temp_clk,
                                          instname=iret.name, template_libname=ret_libname,
                                          inst_pin_prefix=['clk'+str(2*i+1) for i in range(int(num_slices/2))], xy_grid_type='xgrid')
    pdict_m3m4_temp_clk = laygen.get_inst_pin_coord(None, None, rg_m3m4_temp_clk)
    for i in range(int(num_slices/2)):
        for j in range(4):
            laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4], 
                            xy0=pdict_m4m5[isar.name]['CLKO'+str(2*i+1)][0], 
                            xy1=pdict_m3m4_temp_clk[iret.name]['clk'+str(2*i+1)][0], 
                            track_y=pdict_m4m5[isar.name]['CLKO0'][0][1]+num_bits*2+2+2*j, 
                            gridname=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4_temp_clk, extendl=0, extendr=0)
        r=laygen.route(None, layer=laygen.layers['metal'][3], xy0=pdict_m3m4_temp_clk[iret.name]['clk'+str(2*i+1)][0], 
                        xy1=np.array([pdict_m3m4_temp_clk[iret.name]['clk'+str(2*i+1)][0][0], 
                                      pdict_m4m5[isar.name]['CLKO0'][0][1]+num_bits*2+2+2*4+1]), gridname0=rg_m3m4_temp_clk)
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
    ret_libname = 'adc_retimer_ec'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.load_template(filename=ret_libname+'.yaml', libname=ret_libname)
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
    rg_m3m4_thick = 'route_M3_M4_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m5m6_thick2_thick = 'route_M5_M6_thick2_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m6m7_thick2_thick = 'route_M6_M7_thick2_thick'
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

    cellname = 'tisaradc_body_'+str(num_bits)+'b_array_'+str(num_slices)+'slice'
    tisar_core_name = 'tisaradc_body_'+str(num_bits)+'b_array_'+str(num_slices)+'slice_core'
    tisar_space_name = 'tisaradc_body_space'

    #sar generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_body(laygen, objectname_pfix='TISA0', 
                           libname=workinglib, tisar_core_name=tisar_core_name, tisar_space_name=tisar_space_name,
                           placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m5m6=rg_m5m6,
                           routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, 
                           routing_grid_m6m7_thick=rg_m6m7_thick, num_bits=num_bits, num_slices=num_slices, origin=np.array([0, 0]))
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
