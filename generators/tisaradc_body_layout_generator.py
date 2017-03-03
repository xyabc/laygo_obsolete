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

def generate_tisaradc_body(laygen, objectname_pfix, workinglib, ret_libname, sar_libname, sh_libname, ret_name, sar_name, sh_name,
                           placement_grid,
                           routing_grid_m3m4, routing_grid_m4m5, routing_grid_m5m6, routing_grid_m5m6_thick, 
                           routing_grid_m5m6_thick_basic, routing_grid_m5m6_thick2_thick, 
                           routing_grid_m6m7_thick, routing_grid_m6m7_thick2_thick,
                           num_bits=9, num_slices=8, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    rg_m5m6_thick2_thick= routing_grid_m5m6_thick2_thick
    rg_m6m7_thick = routing_grid_m6m7_thick

    # placement
    # ret/sar/sh
    iret=laygen.place(name="I" + objectname_pfix + 'RET0', templatename=ret_name,
                      gridname=pg, xy=origin, template_libname=ret_libname)
    isar = laygen.relplace(name="I" + objectname_pfix + 'SAR0', templatename=sar_name,
                          gridname=pg, refinstname=iret.name, direction='top', template_libname=workinglib)
    pdict_m3m4=laygen.get_inst_pin_coord(None, None, rg_m3m4)
    pdict_m4m5=laygen.get_inst_pin_coord(None, None, rg_m4m5)
    pdict_m5m6=laygen.get_inst_pin_coord(None, None, rg_m5m6)
    pdict_m5m6_thick=laygen.get_inst_pin_coord(None, None, rg_m5m6_thick)
    pdict_m5m6_thick_basic=laygen.get_inst_pin_coord(None, None, rg_m5m6_thick_basic)
    pdict_m5m6_thick2_thick=laygen.get_inst_pin_coord(None, None, rg_m5m6_thick2_thick)
    #sar_array VDD/VSS pin
    laygenhelper.generate_power_rails_from_rails_inst(laygen, routename_tag='_M7_SAR_', layer=laygen.layers['pin'][7], gridname=rg_m6m7_thick, 
                                                      netnames=['VDD', 'VSS'], direction='y', input_rails_instname=isar.name, 
                                                      input_rails_pin_prefix=['VDD', 'VSS'], generate_pin=True,
                                                      overwrite_start_coord=0, overwrite_end_coord=None, 
                                                      offset_route_start=2, offset_route_end=-2)
    laygenhelper.generate_power_rails_from_rails_inst(laygen, routename_tag='_M7_RET_', layer=laygen.layers['metal'][7], gridname=rg_m6m7_thick2_thick, 
                                                      netnames=['VDD', 'VSS'], direction='y', input_rails_instname=iret.name, 
                                                      input_rails_pin_prefix=['VDD', 'VSS'], generate_pin=False,
                                                      overwrite_start_coord=None, overwrite_end_coord=None, 
                                                      offset_route_start=2, offset_route_end=-2)
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
    '''
    #sar-retimer routes (clk)
    clk_ret_phase=[1,3,5,7]
    for i in clk_ret_phase:
        laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4], 
                        xy0=pdict_m4m5[isar.name]['CLKOUT'+str(i)][0], xy1=pdict_m4m5[iret.name]['clk'+str(i)][0], gridname=rg_m4m5)
    '''
    '''
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
        pdict_m5m6_thick_basic.append(laygen.get_inst_pin_coord(None, None, rg_m5m6_thick_basic, index=np.array([i, 0])))

    for i in range(num_slices):
        laygen.pin(name='INP' + str(i), layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['INP'], gridname=rg_m5m6)
        laygen.pin(name='INM' + str(i), layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['INM'], gridname=rg_m5m6)
        laygen.pin(name='CLK' + str(i), layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['CLK'], gridname=rg_m5m6)
        laygen.pin(name='OSP' + str(i), layer=laygen.layers['pin'][3], xy=pdict_m3m4[i][isar.name]['OSP'], gridname=rg_m3m4)
        laygen.pin(name='OSM' + str(i), layer=laygen.layers['pin'][3], xy=pdict_m3m4[i][isar.name]['OSM'], gridname=rg_m3m4)
        laygen.pin(name='VREF' + str(i) + '<0>', layer=laygen.layers['pin'][4], xy=pdict_m5m6[i][isar.name]['VREF<0>'], gridname=rg_m4m5)
        laygen.pin(name='VREF' + str(i) + '<1>', layer=laygen.layers['pin'][4], xy=pdict_m5m6[i][isar.name]['VREF<1>'], gridname=rg_m4m5)
        laygen.pin(name='VREF' + str(i) + '<2>', layer=laygen.layers['pin'][4], xy=pdict_m5m6[i][isar.name]['VREF<2>'], gridname=rg_m4m5)
        laygen.pin(name='ASCLKD' + str(i) + '<0>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['CKDSEL0<0>'], gridname=rg_m5m6)
        laygen.pin(name='ASCLKD' + str(i) + '<1>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['CKDSEL0<1>'], gridname=rg_m5m6)
        laygen.pin(name='ASCLKD' + str(i) + '<2>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['CKDSEL1<0>'], gridname=rg_m5m6)
        laygen.pin(name='ASCLKD' + str(i) + '<3>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['CKDSEL1<1>'], gridname=rg_m5m6)
        laygen.pin(name='EXTCLK' + str(i), layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['EXTCLK'], gridname=rg_m5m6)
        laygen.pin(name='EXTSEL_CLK' + str(i), layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['EXTSEL_CLK'], gridname=rg_m5m6)
        for j in range(num_bits):
            laygen.pin(name='ADCOUT' + str(i) + '<'+str(j)+'>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[i][isar.name]['ADCOUT<'+str(j)+'>'], gridname=rg_m5m6)
    #VDD/VSS pin
    vddcnt=0
    vsscnt=0
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
    ret_libname = 'adc_retimer_ec'
    sh_libname = 'adc_sampler_ec'
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
    rg_m4m5 = 'route_M4_M5_basic'
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
    #sar generation
    cellname = 'tisaradc_body_'+str(num_bits)+'b_array_'+str(num_slices)+'slice'
    sar_name = 'sar_'+str(num_bits)+'b_array_'+str(num_slices)+'slice'
    ret_name = 'adc_retimer'
    sh_name = 'adc_frontend_sampler_array'

    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_body(laygen, objectname_pfix='TISA0', workinglib=workinglib,
                 ret_libname=ret_libname,
                 sar_libname=workinglib,
                 sh_libname=sh_libname,
                 ret_name=ret_name,
                 sar_name=sar_name,
                 sh_name=sh_name,
                 placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m5m6=rg_m5m6,
                 routing_grid_m5m6_thick=rg_m5m6_thick, 
                 routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, routing_grid_m5m6_thick2_thick=rg_m5m6_thick2_thick,
                 routing_grid_m6m7_thick=rg_m6m7_thick, routing_grid_m6m7_thick2_thick=rg_m6m7_thick2_thick,
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
