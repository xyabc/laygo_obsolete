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

def generate_tisaradc_space(laygen, objectname_pfix, tisar_libname, space_libname, tisar_name, space_name,
                            placement_grid, routing_grid_m3m4_thick, routing_grid_m4m5_thick, routing_grid_m5m6_thick, 
                            origin=np.array([0, 0])):
    """generate tisar space """
    pg = placement_grid
    ttisar = laygen.templates.get_template(tisar_name, libname=tisar_libname)
    tspace = laygen.templates.get_template(space_name, libname=space_libname)
    tbnd_bottom = laygen.templates.get_template('boundary_bottom')
    tbnd_bleft = laygen.templates.get_template('boundary_bottomleft')
    #space_xy=np.array([tspace.size[0], ttisar.size[1]])
    space_xy=np.array([tspace.size[0], 69.408]) #change it after finishing the clock part
    laygen.add_rect(None, np.array([origin, origin+space_xy+2*tbnd_bleft.size[0]*np.array([1, 0])]), laygen.layers['prbnd'])
    #num_space=int((ttisar.size[1]-2*tbnd_bottom.size[1])/tspace.size[1])
    num_space=int((69.408-2*tbnd_bottom.size[1])/tspace.size[1]) #should be changed after finishing the clock part
    space_origin = origin + laygen.get_template_size('boundary_bottomleft', pg)
    ispace = [laygen.place(name="I" + objectname_pfix + 'SP0', templatename=space_name,
                          gridname=pg, xy=space_origin, template_libname=space_libname)]
    #devname_bnd_left = ['nmos4_fast_left', 'pmos4_fast_left']
    #devname_bnd_right = ['nmos4_fast_right', 'pmos4_fast_right']
    devname_bnd_left = ['ptap_fast_left', 'ntap_fast_left']
    devname_bnd_right = ['ptap_fast_right', 'ntap_fast_right']
    transform_bnd_left = ['R0', 'MX']
    transform_bnd_right = ['R0', 'MX']
    for i in range(1, num_space):
        if i % 2 == 0:
            ispace.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace[-1].name, direction='top', transform='R0',
                                       template_libname=space_libname))
            #devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            #devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            devname_bnd_left += ['ptap_fast_left', 'ntap_fast_left']
            devname_bnd_right += ['ptap_fast_right', 'ntap_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            ispace.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace[-1].name, direction='top', transform='MX',
                                       template_libname=space_libname))
            #devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            #devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            devname_bnd_left += ['ntap_fast_left', 'ptap_fast_left']
            devname_bnd_right += ['ntap_fast_right', 'ptap_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
            #transform_bnd_left +=  ['MX', 'R0']
            #transform_bnd_right += ['MX', 'R0']
        
    m_bnd = int(space_xy[0] / tbnd_bottom.size[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = laygenhelper.generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=devname_bnd_left,
                            transform_left=transform_bnd_left,
                            devname_right=devname_bnd_right,
                            transform_right=transform_bnd_right,
                            origin=origin)
    #vdd/vss
    #m3
    rvdd_xy_m3=[]
    rvss_xy_m3=[]
    space_template = laygen.templates.get_template(space_name, workinglib)
    space_pins=space_template.pins
    space_origin_phy = laygen.get_inst_bbox_phygrid(ispace[0].name)[0]
    vddcnt=0
    vsscnt=0
    for pn, p in space_pins.items():
        if pn.startswith('VDD'):
            pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space])])
            laygen.add_rect(None, pxy, p['layer'])
            rvdd_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
            vddcnt += 1
        if pn.startswith('VSS'):
            pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space])])
            laygen.add_rect(None, pxy, p['layer'])
            rvss_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
            vsscnt += 1
    #m4
    input_rails_xy = [rvdd_xy_m3, rvss_xy_m3]
    rvdd_m4, rvss_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_M4_', layer=laygen.layers['metal'][4], 
                                        gridname=rg_m3m4_thick, netnames=['VDD', 'VSS'], direction='x', 
                                        input_rails_xy=input_rails_xy, generate_pin=False, 
                                        overwrite_start_coord=None, overwrite_end_coord=None, 
                                        overwrite_num_routes=None, offset_start_index=0, offset_end_index=0)
    #m5
    input_rails_rect = [rvdd_m4, rvss_m4]
    rvdd_m5, rvss_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M5_', 
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    #m6 (extract VDD/VSS grid from tisar and make power pins)
    rg_m5m6_thick_temp_tisar='route_M5_M6_thick_temp_tisar_VDD'
    laygenhelper.generate_grids_from_template(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_tisar, 
                                              template_name=tisar_name, template_libname=tisar_libname,
                                              template_pin_prefix=['VDD'], xy_grid_type='ygrid')
    input_rails_rect = [rvdd_m5]
    rvdd_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_', 
                layer=laygen.layers['pin'][6], gridname=rg_m5m6_thick_temp_tisar, netnames=['VDD'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=-1)
    rg_m5m6_thick_temp_tisar='route_M5_M6_thick_temp_tisar_VSS'
    laygenhelper.generate_grids_from_template(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_tisar, 
                                              template_name=tisar_name, template_libname=tisar_libname,
                                              template_pin_prefix=['VSS'], xy_grid_type='ygrid')
    input_rails_rect = [rvss_m5]
    rvss_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_', 
                layer=laygen.layers['pin'][6], gridname=rg_m5m6_thick_temp_tisar, netnames=['VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=-2)


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

    cellname = 'tisaradc_body_space'
    tisar_name = 'tisaradc_body_'+str(num_bits)+'b_array_'+str(num_slices)+'slice_core'
    sar_name = 'sar_wsamp_'+str(num_bits)+'b_array_'+str(num_slices)+'slice'
    sh_name = 'adc_frontend_sampler_array'
    #space_name = 'space'
    space_name = 'space_tap'

    #space cell generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_space(laygen, objectname_pfix='TISASP0', tisar_libname=workinglib, space_libname=workinglib, 
                            tisar_name=tisar_name, space_name=space_name, placement_grid=pg, 
                            routing_grid_m3m4_thick=rg_m3m4_thick, 
                            routing_grid_m4m5_thick=rg_m4m5_thick, 
                            routing_grid_m5m6_thick=rg_m5m6_thick, 
                            origin=np.array([0, 0]))
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
