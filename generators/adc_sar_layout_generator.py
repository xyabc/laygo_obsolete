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
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_sar(laygen, objectname_pfix, workinglib, sarabe_name, sarafe_name, 
                 placement_grid,
                 routing_grid_m3m4, routing_grid_m4m5, routing_grid_m5m6, routing_grid_m5m6_thick, num_bits=8, origin=np.array([0, 0])):
    """generate sar"""
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick

    # placement
    #abe
    iabe=laygen.place(name="I" + objectname_pfix + 'ABE0', templatename=sarabe_name,
                      gridname=pg, xy=origin, template_libname=workinglib)
    yabe=laygen.get_template_size(name=sarabe_name, gridname=pg, libname=workinglib)[1]
    #afe
    iafe=laygen.relplace(name="I" + objectname_pfix + 'AFE0', templatename=sarafe_name,
                         gridname=pg, refinstname=iabe.name, direction='top', template_libname=workinglib)

    #reference coordinates
    pdict_m3m4 = laygen.get_inst_pin_coord(None, None, rg_m3m4)
    pdict_m4m5 = laygen.get_inst_pin_coord(None, None, rg_m4m5)
    pdict_m5m6 = laygen.get_inst_pin_coord(None, None, rg_m5m6)
    pdict_m5m6_thick = laygen.get_inst_pin_coord(None, None, rg_m5m6_thick)

    #zp/zm/zmid route
    x0=pdict_m5m6[iafe.name]['ENL0<0>'][0][0]+8
    y0=pdict_m5m6[iabe.name]['ZP<0>'][1][1]
    for i in range(1, num_bits):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[iabe.name]['ZP<'+str(i)+'>'][0],
                                           np.array([x0+3*i+2, y0 + 3*num_bits]),
                                           y0+i+0*num_bits, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[iabe.name]['ZM<'+str(i)+'>'][0],
                                           np.array([x0+3*i+1, y0 + 3*num_bits]),
                                           y0+i+1*num_bits, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[iabe.name]['ZMID<'+str(i)+'>'][0],
                                           np.array([x0+3*i+0, y0 + 3*num_bits]),
                                           y0+i+2*num_bits, rg_m5m6)
        #ZP-ENL/R
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+2, y0 + 3*num_bits]),
                                           pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<0>'][0],
                                           y0+i+3*num_bits+2, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+2, y0 + 3*num_bits]),
                                           pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<2>'][0],
                                           y0+i+3*num_bits+2, rg_m5m6)
        #ZM-ENL/R
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+1, y0 + 3*num_bits]),
                                           pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<2>'][0],
                                           y0+i+4*num_bits+2, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+1, y0 + 3*num_bits]),
                                           pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<0>'][0],
                                           y0+i+4*num_bits+2, rg_m5m6)
        #ZMID-ENL/R
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+0, y0 + 3*num_bits]),
                                           pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<1>'][0],
                                           y0+i+5*num_bits+2, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+0, y0 + 3*num_bits]),
                                           pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<1>'][0],
                                           y0+i+5*num_bits+2, rg_m5m6)
    #saop/saom route
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iabe.name]['SAOPB'][0], pdict_m5m6[iafe.name]['OUTM'][0],
                                       y0 + 6*num_bits+4, rg_m5m6)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iabe.name]['SAOMB'][0], pdict_m5m6[iafe.name]['OUTP'][0],
                                       y0 + 6*num_bits+5, rg_m5m6)
    #sarclkb
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iabe.name]['SARCLKB'][0], pdict_m5m6[iafe.name]['CLKB'][0],
                                       y0 + 6*num_bits+6, rg_m5m6)
    #VDD/VSS pin
    i=0
    for p, pxy in pdict_m5m6_thick[iabe.name].items():
        if p.startswith('VDD_M6'):
            laygen.pin(name='VDD' + str(i), layer=laygen.layers['pin'][6], xy=pxy, gridname=rg_m5m6_thick, netname='VDD')
            i+=1
    for p, pxy in pdict_m5m6_thick[iafe.name].items():
        if p.startswith('VDD_M6'):
            laygen.pin(name='VDD' + str(i), layer=laygen.layers['pin'][6], xy=pxy, gridname=rg_m5m6_thick, netname='VDD')
            i+=1
    i=0
    for p, pxy in pdict_m5m6_thick[iabe.name].items():
        if p.startswith('VSS_M6'):
            laygen.pin(name='VSS' + str(i), layer=laygen.layers['pin'][6], xy=pxy, gridname=rg_m5m6_thick, netname='VSS')
            i+=1
    for p, pxy in pdict_m5m6_thick[iafe.name].items():
        if p.startswith('VSS_M6'):
            laygen.pin(name='VSS' + str(i), layer=laygen.layers['pin'][6], xy=pxy, gridname=rg_m5m6_thick, netname='VSS')
            i+=1
    #inp/inm
    laygen.pin(name='INP', layer=laygen.layers['pin'][6], xy=pdict_m5m6[iafe.name]['INP'], gridname=rg_m5m6)
    laygen.pin(name='INM', layer=laygen.layers['pin'][6], xy=pdict_m5m6[iafe.name]['INM'], gridname=rg_m5m6)
    #osp/osm
    laygen.pin(name='OSP', layer=laygen.layers['pin'][3], xy=pdict_m3m4[iafe.name]['OSP'], gridname=rg_m3m4)
    laygen.pin(name='OSM', layer=laygen.layers['pin'][3], xy=pdict_m3m4[iafe.name]['OSM'], gridname=rg_m3m4)
    #vref
    laygen.pin(name='VREF<0>', layer=laygen.layers['pin'][4], xy=pdict_m3m4[iafe.name]['VREF<0>'], gridname=rg_m3m4)
    laygen.pin(name='VREF<1>', layer=laygen.layers['pin'][4], xy=pdict_m3m4[iafe.name]['VREF<1>'], gridname=rg_m3m4)
    laygen.pin(name='VREF<2>', layer=laygen.layers['pin'][4], xy=pdict_m3m4[iafe.name]['VREF<2>'], gridname=rg_m3m4)
    laygen.pin(name='VREF_M5L<0>', layer=laygen.layers['pin'][5], xy=pdict_m4m5[iafe.name]['VREF_M5L<0>'], gridname=rg_m4m5, netname='VREF<0>')
    laygen.pin(name='VREF_M5L<1>', layer=laygen.layers['pin'][5], xy=pdict_m4m5[iafe.name]['VREF_M5L<1>'], gridname=rg_m4m5, netname='VREF<1>')
    laygen.pin(name='VREF_M5L<2>', layer=laygen.layers['pin'][5], xy=pdict_m4m5[iafe.name]['VREF_M5L<2>'], gridname=rg_m4m5, netname='VREF<2>')
    laygen.pin(name='VREF_M5R<0>', layer=laygen.layers['pin'][5], xy=pdict_m4m5[iafe.name]['VREF_M5R<0>'], gridname=rg_m4m5, netname='VREF<0>')
    laygen.pin(name='VREF_M5R<1>', layer=laygen.layers['pin'][5], xy=pdict_m4m5[iafe.name]['VREF_M5R<1>'], gridname=rg_m4m5, netname='VREF<1>')
    laygen.pin(name='VREF_M5R<2>', layer=laygen.layers['pin'][5], xy=pdict_m4m5[iafe.name]['VREF_M5R<2>'], gridname=rg_m4m5, netname='VREF<2>')
    #vol/vor
    for i in range(num_bits-1):
        laygen.pin(name='VOL<'+str(i)+'>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iafe.name]['VOL<'+str(i)+'>'], gridname=rg_m5m6)
        laygen.pin(name='VOR<'+str(i)+'>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iafe.name]['VOR<'+str(i)+'>'], gridname=rg_m5m6)
    #adcout
    for i in range(num_bits):
        laygen.pin(name='ADCOUT<'+str(i)+'>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iabe.name]['ADCOUT<'+str(i)+'>'], gridname=rg_m5m6)
    #clk
    laygen.pin(name='CLK', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iabe.name]['RST'], gridname=rg_m5m6)
    laygen.pin(name='CLKOUT', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iabe.name]['RSTOUT'], gridname=rg_m5m6, netname='CLK')
    #clkprb
    laygen.pin(name='CLKPRB', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iabe.name]['CLKPRB'], gridname=rg_m5m6)
    #extclk/extclksel
    laygen.pin(name='EXTCLK', layer=laygen.layers['pin'][5], xy=pdict_m4m5[iabe.name]['EXTCLK'], gridname=rg_m4m5)
    laygen.pin(name='EXTSEL_CLK', layer=laygen.layers['pin'][5], xy=pdict_m4m5[iabe.name]['EXTSEL_CLK'], gridname=rg_m4m5)
    #ckdsel
    for i in range(2):
        laygen.pin(name='CKDSEL0<' + str(i) + '>', layer=laygen.layers['pin'][5],
                   xy=pdict_m4m5[iabe.name]['CKDSEL0<' + str(i) + '>'], gridname=rg_m4m5)
        laygen.pin(name='CKDSEL1<' + str(i) + '>', layer=laygen.layers['pin'][5],
                   xy=pdict_m4m5[iabe.name]['CKDSEL1<' + str(i) + '>'], gridname=rg_m4m5)
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
    cellname='sar_'+str(num_bits)+'b'
    sarabe_name = 'sarabe_dualdelay_'+str(num_bits)+'b'
    sarafe_name = 'sarafe_nsw_'+str(num_bits-1)+'b'

    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sar(laygen, objectname_pfix='SA0', workinglib=workinglib, sarabe_name=sarabe_name, sarafe_name=sarafe_name,
                 placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m5m6=rg_m5m6,
                 routing_grid_m5m6_thick=rg_m5m6_thick,
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
