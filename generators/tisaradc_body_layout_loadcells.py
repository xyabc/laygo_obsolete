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
#import logging;logging.basicConfig(level=logging.DEBUG)

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
    saradctemplib = 'adc_sar_generated'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.load_template(filename=saradctemplib+'.yaml', libname=saradctemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    import bag
    prj = bag.BagProject()
    #lib_list = ['adc_retimer_ec', 'adc_sampler_ec']
    #cell_list = ['adc_retimer', 'frontend_sampler_array']
    #workinglib = 'adc_sar_generated'

    workinglib = 'adc_retimer_ec'
    workingcell = 'adc_retimer'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    db = laygen.import_BAG(prj, workinglib, workingcell)
    #laygen.display()
    laygen.add_template_from_cell()
    laygen.construct_template_and_grid(db, workinglib, cellname=workingcell, layer_boundary=laygen.layers['prbnd'])
    #update boundary - hack: infer xy dimension from topright boundary cell
    for instname, inst in laygen.db.design['adc_retimer_ec']['adc_retimer']['instances'].items():
        if inst.cellname=='boundary_topright':
            ixy = inst.xy
            laygen.templates.templates['adc_retimer_ec']['adc_retimer'].xy[1] = \
                ixy + laygen.templates.templates[utemplib]['boundary_topright'].xy[1]
    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)
    '''
    #load from preset
    load_from_file=True
    yamlfile_system_input="adc_sar_dsn_system_input.yaml"
    if load_from_file==True:
        with open(yamlfile_system_input, 'r') as stream:
            sysdict_i = yaml.load(stream)
        num_bits=sysdict_i['n_bit']
        num_slices=sysdict_i['n_interleave']
    #sar generation
    cellname = 'tisaradc_'+str(num_bits)+'b_array_'+str(num_slices)+'slice'
    ret_name = 'adc_retimer'
    sar_name = 'sar_'+str(num_bits)+'b_array_'+str(num_slices)+'slice'
    sh_name = 'sh'

    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sar_array(laygen, objectname_pfix='TISA0', workinglib=workinglib, ret_name=ret_name, sar_name=sar_name, sh_name=sh_name
                 placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m5m6=rg_m5m6,
                 routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic,
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
    '''
