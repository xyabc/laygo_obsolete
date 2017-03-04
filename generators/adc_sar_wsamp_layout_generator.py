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
                       routing_grid_m5m6_thick,
                       num_bits=9, origin=np.array([0, 0])):
    """generate sar with sampling frontend """
    pg = placement_grid

    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick

    # placement
    # sar
    isar=laygen.place(name="I" + objectname_pfix + 'SAR0', templatename=sar_name,
                      gridname=pg, xy=origin, template_libname=workinglib)
    isamp = laygen.relplace(name="I" + objectname_pfix + 'SAMP0', templatename=samp_name,
                          gridname=pg, refinstname=isar.name, direction='top', template_libname=samp_lib)

    #reference coordinates
    pdict_m5m6=laygen.get_inst_pin_coord(None, None, rg_m5m6)
    pdict_m5m6_thick=laygen.get_inst_pin_coord(None, None, rg_m5m6_thick)

    #VDD/VSS pin
    vddcnt=0
    vsscnt=0
    for p in pdict_m5m6[isar.name]:
        if p.startswith('VDD'):
            xy0=pdict_m5m6_thick[isar.name][p]
            laygen.pin(name='VDD' + str(vddcnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VDD')
            vddcnt+=1
        if p.startswith('VSS'):
            xy0=pdict_m5m6_thick[isar.name][p]
            laygen.pin(name='VSS' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VSS')
            vsscnt+=1

    rg_m5m6_thick_samp='route_M5_M6_thick_temp_samp'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_samp,
                                          instname=isamp.name, template_libname=samp_lib,
                                          inst_pin_prefix=['VDD', 'VSS'], xy_grid_type='ygrid')
    pdict_m5m6_thick2 = laygen.get_inst_pin_coord(None, None, rg_m5m6_thick_samp)

    for p in pdict_m5m6_thick2[isamp.name]:
        if p.startswith('VDD'):
            xy0=pdict_m5m6_thick2[isamp.name][p]
            laygen.pin(name='VDD' + str(vddcnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_samp, netname='VDD')
            vddcnt+=1
        if p.startswith('VSS'):
            xy0=pdict_m5m6_thick2[isamp.name][p]
            laygen.pin(name='VSS' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_samp, netname='VSS')
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
                       placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m5m6=rg_m5m6,
                       routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick,
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
