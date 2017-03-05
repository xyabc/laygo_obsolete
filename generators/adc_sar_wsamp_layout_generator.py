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

def generate_sar_wsamp(laygen, objectname_pfix, workinglib, samp_lib, sar_name, samp_name,
                       placement_grid, routing_grid_m5m6,
                       routing_grid_m5m6_thick, routing_grid_m5m6_thick_basic,
                       num_bits=9, origin=np.array([0, 0])):
    """generate sar with sampling frontend """
    pg = placement_grid

    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic #for clock routing

    # placement
    # sar
    isar=laygen.place(name="I" + objectname_pfix + 'SAR0', templatename=sar_name,
                      gridname=pg, xy=origin, template_libname=workinglib)
    # samp
    isamp = laygen.relplace(name="I" + objectname_pfix + 'SAMP0', templatename=samp_name,
                          gridname=pg, refinstname=isar.name, direction='top', template_libname=samp_lib)

    # template handles
    sar_template = laygen.templates.get_template(sar_name, workinglib)
    samp_template = laygen.templates.get_template(samp_name, samp_lib)

    #reference coordinates
    pdict_m5m6=laygen.get_inst_pin_coord(None, None, rg_m5m6)
    pdict_m5m6_thick=laygen.get_inst_pin_coord(None, None, rg_m5m6_thick)
    sar_pins=sar_template.pins
    samp_pins=samp_template.pins
    sar_xy=isar.xy[0]
    samp_xy=isamp.xy[0]

    #signal route (clk/inp/inm)
    #make virtual grids and route on the grids (assuming drc clearance of each block)
    rg_m5m6_thick_basic_temp_sig='route_M5_M6_thick_basic_temp_sig'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick_basic, gridname_output=rg_m5m6_thick_basic_temp_sig,
                                          instname=isamp.name, template_libname=samp_lib,
                                          inst_pin_prefix=['ckout', 'outp', 'outn'], xy_grid_type='xgrid')
    pdict_m5m6_thick_basic_temp_sig = laygen.get_inst_pin_coord(None, None, rg_m5m6_thick_basic_temp_sig)
    #clock
    rclk0 = laygen.route(None, laygen.layers['metal'][5],
                         xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['ckout'][0],
                         xy1=pdict_m5m6_thick_basic_temp_sig[isar.name]['CLK'][1]-np.array([0,1]), gridname0=rg_m5m6_thick_basic_temp_sig)
    laygen.via(None,pdict_m5m6_thick_basic_temp_sig[isar.name]['CLK'][1], rg_m5m6_thick_basic_temp_sig)

    #frontend sig
    inp_y_list=[]
    inm_y_list=[]
    for pn, p in pdict_m5m6_thick_basic_temp_sig[isar.name].items():
        if pn.startswith('INP'):
            inp_y_list.append(p[0][1])
            laygen.via(None,p[0], rg_m5m6_thick_basic_temp_sig)
        if pn.startswith('INM'):
            inm_y_list.append(p[0][1])
            laygen.via(None,p[0], rg_m5m6_thick_basic_temp_sig)
    inp_y=min(inp_y_list)
    inm_y=min(inm_y_list)
    rinp0 = laygen.route(None, laygen.layers['metal'][5],
                         xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['outp'][0],
                         xy1=np.array([pdict_m5m6_thick_basic_temp_sig[isar.name]['INP0'][0][0],inp_y-1]), 
                         gridname0=rg_m5m6_thick_basic_temp_sig)
    rinp0 = laygen.route(None, laygen.layers['metal'][5],
                         xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['outn'][0],
                         xy1=np.array([pdict_m5m6_thick_basic_temp_sig[isar.name]['INM0'][0][0],inm_y-1]), 
                         gridname0=rg_m5m6_thick_basic_temp_sig)

    #input pins (just duplicate from lower hierarchy cells)
    laygen.add_pin('CLK', 'CLK', samp_xy+samp_pins['ckin']['xy'], samp_pins['ckin']['layer'])
    laygen.add_pin('INP', 'INP', samp_xy+samp_pins['inp']['xy'], samp_pins['ckin']['layer'])
    laygen.add_pin('INM', 'INM', samp_xy+samp_pins['inn']['xy'], samp_pins['ckin']['layer'])

    laygen.add_pin('OSP', 'OSP', sar_xy+sar_pins['OSP']['xy'], sar_pins['OSP']['layer'])
    laygen.add_pin('OSM', 'OSM', sar_xy+sar_pins['OSM']['xy'], sar_pins['OSM']['layer'])
    #laygen.add_pin('VREF<2>', 'VREF<2>', sar_xy+sar_pins['VREF<2>']['xy'], sar_pins['VREF<2>']['layer'])
    #laygen.add_pin('VREF<1>', 'VREF<1>', sar_xy+sar_pins['VREF<1>']['xy'], sar_pins['VREF<1>']['layer'])
    #laygen.add_pin('VREF<0>', 'VREF<0>', sar_xy+sar_pins['VREF<0>']['xy'], sar_pins['VREF<0>']['layer'])
    laygen.add_pin('VREF_M5R<2>', 'VREF<2>', sar_xy+sar_pins['VREF_M5R<2>']['xy'], sar_pins['VREF_M5R<2>']['layer'])
    laygen.add_pin('VREF_M5R<1>', 'VREF<1>', sar_xy+sar_pins['VREF_M5R<1>']['xy'], sar_pins['VREF_M5R<1>']['layer'])
    laygen.add_pin('VREF_M5R<0>', 'VREF<0>', sar_xy+sar_pins['VREF_M5R<0>']['xy'], sar_pins['VREF_M5R<0>']['layer'])
    laygen.add_pin('VREF_M5L<2>', 'VREF<2>', sar_xy+sar_pins['VREF_M5L<2>']['xy'], sar_pins['VREF_M5L<2>']['layer'])
    laygen.add_pin('VREF_M5L<1>', 'VREF<1>', sar_xy+sar_pins['VREF_M5L<1>']['xy'], sar_pins['VREF_M5L<1>']['layer'])
    laygen.add_pin('VREF_M5L<0>', 'VREF<0>', sar_xy+sar_pins['VREF_M5L<0>']['xy'], sar_pins['VREF_M5L<0>']['layer'])
    laygen.add_pin('CKDSEL0<1>', 'CKDSEL0<1>', sar_xy+sar_pins['CKDSEL0<1>']['xy'], sar_pins['CKDSEL0<1>']['layer'])
    laygen.add_pin('CKDSEL0<0>', 'CKDSEL0<0>', sar_xy+sar_pins['CKDSEL0<0>']['xy'], sar_pins['CKDSEL0<0>']['layer'])
    laygen.add_pin('CKDSEL1<1>', 'CKDSEL1<1>', sar_xy+sar_pins['CKDSEL1<1>']['xy'], sar_pins['CKDSEL1<1>']['layer'])
    laygen.add_pin('CKDSEL1<0>', 'CKDSEL1<0>', sar_xy+sar_pins['CKDSEL1<0>']['xy'], sar_pins['CKDSEL1<0>']['layer'])
    laygen.add_pin('EXTCLK', 'EXTCLK', sar_xy+sar_pins['EXTCLK']['xy'], sar_pins['EXTCLK']['layer'])
    laygen.add_pin('EXTSEL_CLK', 'EXTSEL_CLK', sar_xy+sar_pins['EXTSEL_CLK']['xy'], sar_pins['EXTSEL_CLK']['layer'])
    #output pins (just duplicate from lower hierarchy cells)
    for i in range(num_bits):
        pn='ADCOUT'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
    laygen.add_pin('CLKO', 'CLKO', sar_xy+sar_pins['CLKOUT']['xy'], sar_pins['CLKOUT']['layer'])
    
    #probe pins
    laygen.add_pin('CLKPRB_SAMP', 'CLKPRB_SAMP', samp_xy+samp_pins['ckpg']['xy'], samp_pins['ckpg']['layer'])
    laygen.add_pin('CLKPRB_SAR', 'CLKPRB_SAR', sar_xy+sar_pins['CLKPRB']['xy'], sar_pins['CLKPRB']['layer'])
    laygen.add_pin('SAMPP', 'SAMPP', sar_xy+sar_pins['SAINP']['xy'], sar_pins['SAINP']['layer'])
    laygen.add_pin('SAMPM', 'SAMPM', sar_xy+sar_pins['SAINM']['xy'], sar_pins['SAINM']['layer'])
    laygen.add_pin('SARCLK', 'SARCLK', sar_xy+sar_pins['SARCLK']['xy'], sar_pins['SARCLK']['layer'])
    laygen.add_pin('SARCLKB', 'SARCLKB', sar_xy+sar_pins['SARCLKB']['xy'], sar_pins['SARCLKB']['layer'])
    laygen.add_pin('COMPOUT', 'COMPOUT', sar_xy+sar_pins['COMPOUT']['xy'], sar_pins['COMPOUT']['layer'])
    laygen.add_pin('DONE', 'DONE', sar_xy+sar_pins['DONE']['xy'], sar_pins['DONE']['layer'])
    laygen.add_pin('UP', 'UP', sar_xy+sar_pins['UP']['xy'], sar_pins['UP']['layer'])
    for i in range(num_bits):
        pn='ZP'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        pn='ZMID'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        pn='ZM'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        pn='SB'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
    for i in range(num_bits-1):
        pn='VOL'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        pn='VOR'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])

    #VDD/VSS pin
    vddcnt=0
    vsscnt=0
    for p in pdict_m5m6[isar.name]:
        if p.startswith('VDD'):
            xy0=pdict_m5m6_thick[isar.name][p]
            laygen.pin(name='VDDSAR' + str(vddcnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VDD:')
            vddcnt+=1
        if p.startswith('VSS'):
            xy0=pdict_m5m6_thick[isar.name][p]
            laygen.pin(name='VSSSAR' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VSS:')
            vsscnt+=1
    #extract VDD/VSS grid from samp and make power pins
    rg_m5m6_thick_temp_samp='route_M5_M6_thick_temp_samp'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_samp,
                                          instname=isamp.name, template_libname=samp_lib,
                                          inst_pin_prefix=['VDD', 'VSS'], xy_grid_type='ygrid')
    pdict_m5m6_thick_temp_samp = laygen.get_inst_pin_coord(None, None, rg_m5m6_thick_temp_samp)
    vddcnt=0
    vsscnt=0
    for p in pdict_m5m6_thick_temp_samp[isamp.name]:
        if p.startswith('VDD'):
            xy0=pdict_m5m6_thick_temp_samp[isamp.name][p]
            laygen.pin(name='VDDSAMP' + str(vddcnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_temp_samp, netname='VDD:')
            vddcnt+=1
        if p.startswith('VSS'):
            xy0=pdict_m5m6_thick_temp_samp[isamp.name][p]
            laygen.pin(name='VSSSAMP' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_temp_samp, netname='VSS:')
            vsscnt+=1

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
    samp_lib = 'adc_sampler_ec'
    samp_name = 'sampler_nmos'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.load_template(filename=samp_lib+'.yaml', libname=samp_lib)
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
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=9
    #load from preset
    load_from_file=True
    yamlfile_system_input="adc_sar_dsn_system_input.yaml"
    if load_from_file==True:
        with open(yamlfile_system_input, 'r') as stream:
            sysdict_i = yaml.load(stream)
        num_bits=sysdict_i['n_bit']
    #sar generation
    cellname='sar_wsamp_'+str(num_bits)+'b'
    sar_name = 'sar_'+str(num_bits)+'b'

    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sar_wsamp(laygen, objectname_pfix='SA0', workinglib=workinglib, samp_lib=samp_lib, sar_name=sar_name, samp_name=samp_name,
                       placement_grid=pg, routing_grid_m5m6=rg_m5m6, routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, 
                       num_bits=num_bits, origin=np.array([0, 0]))
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
