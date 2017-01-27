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

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_coord(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_coord(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_coord(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_coord(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_sarfsm(laygen, objectname_pfix, templib_logic, placement_grid,
                    routing_grid_m3m4, num_bits=8, m=2, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate one-hot coded sar fsm """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name='tap'
    tie_name = 'tie_2x'
    dff_name='dff_rsth_'+str(m)+'x'
    inv_name='inv_'+str(m)+'x'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    isp2x=[]
    isp1x=[]
    refi=itapl.name
    if not m_space_2x==0:
        isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X0', templatename=space_2x_name,
                     shape = np.array([m_space_2x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp2x[-1].name
    if not m_space_1x==0:
        isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X0', templatename=space_1x_name,
                     shape=np.array([m_space_1x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp1x[-1].name
    itie0 = laygen.relplace(name = "I" + objectname_pfix + 'TIE0', templatename = tie_name,
                            gridname = pg, refinstname = refi, template_libname = templib_logic)
    idff0 = laygen.relplace(name = "I" + objectname_pfix + 'TRGGEN0', templatename = dff_name,
                            gridname = pg, refinstname = itie0.name, template_libname = templib_logic)
    iinv0 = laygen.relplace(name = "I" + objectname_pfix + 'INV0', templatename = inv_name,
                            gridname = pg, refinstname = idff0.name, template_libname = templib_logic)
    idff=[]
    for i in range(num_bits-1):
        if i==0:
            refi = iinv0.name
        else:
            refi = idff[-1].name
        idff.append(laygen.relplace(name = "I" + objectname_pfix + 'DFF' + str(i), templatename = dff_name,
                                    gridname = pg, refinstname = refi, template_libname = templib_logic))
    itapr=laygen.relplace(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                          gridname = pg, refinstname = idff[-1].name, template_libname = templib_logic)
    #internal pins
    itie0_tievss_xy=laygen.get_inst_pin_coord(itie0.name, 'TIEVSS', rg_m3m4)
    idff0_i_xy=laygen.get_inst_pin_coord(idff0.name, 'I', rg_m3m4)
    idff0_rst_xy=laygen.get_inst_pin_coord(idff0.name, 'RST', rg_m3m4)
    idff0_clk_xy=laygen.get_inst_pin_coord(idff0.name, 'CLK', rg_m3m4)
    idff0_o_xy=laygen.get_inst_pin_coord(idff0.name, 'O', rg_m3m4)
    iinv0_i_xy=laygen.get_inst_pin_coord(iinv0.name, 'I', rg_m3m4)
    iinv0_o_xy=laygen.get_inst_pin_coord(iinv0.name, 'O', rg_m3m4)
    idff_i_xy = []
    idff_rst_xy = []
    idff_clk_xy = []
    idff_o_xy = []
    for i in range(num_bits-1):
        idff_i_xy.append(laygen.get_inst_pin_coord(idff[i].name, 'I', rg_m3m4))
        idff_rst_xy.append(laygen.get_inst_pin_coord(idff[i].name, 'RST', rg_m3m4))
        idff_clk_xy.append(laygen.get_inst_pin_coord(idff[i].name, 'CLK', rg_m3m4))
        idff_o_xy.append(laygen.get_inst_pin_coord(idff[i].name, 'O', rg_m3m4))
    #codepath
    y0 = idff0_i_xy[0][1]+2
    x1 = laygen.get_inst_xy(name=idff[-1].name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=idff[-1].cellname, gridname=rg_m3m4, libname=templib_logic)[0] - 1
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], idff0_o_xy[0], iinv0_i_xy[0], y0-2, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], iinv0_o_xy[0], idff_i_xy[0][0], y0+0, rg_m3m4)
    rsb=[]
    for i in range(num_bits-2):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], idff_o_xy[i][0], idff_i_xy[i+1][0], y0+0, rg_m3m4)
        rsb.append(rh0)
    rv0, rsb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], idff_o_xy[-1][0],
                                  np.array([x1, y0 - 2]), rg_m3m4)
    rsb.append(rsb0)
    #tie
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], itie0_tievss_xy[0], idff0_i_xy[0], y0+0, rg_m3m4)
    #clock
    [rv0, rclk0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], idff0_clk_xy[0], idff_clk_xy[0][0], y0+1, rg_m3m4)
    for i in range(num_bits-2):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], idff_clk_xy[i][0], idff_clk_xy[i+1][0], y0+1, rg_m3m4)
    #rst
    [rv0, rrst0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], idff0_rst_xy[0], idff_rst_xy[0][0], y0+2, rg_m3m4)
    for i in range(num_bits-2):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], idff_rst_xy[i][0], idff_rst_xy[i+1][0], y0+2, rg_m3m4)

    #pins
    for i, r in enumerate(rsb):
        laygen.create_boundary_pin_form_rect(r, rg_m3m4, 'SB<'+str(num_bits-2-i)+'>', laygen.layers['pin'][4], size=4, direction='right')
        #laygen.pin(name='SB<'+str(num_bits-2-i)+'>', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(r.name, rg_m3m4), gridname=rg_m3m4)

    laygen.create_boundary_pin_form_rect(rrst0, rg_m3m4, "RST", laygen.layers['pin'][4], size=4, direction='left')
    laygen.create_boundary_pin_form_rect(rclk0, rg_m3m4, "CLK", laygen.layers['pin'][4], size=4, direction='left')

    # power pin
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=itapl, inst_right=itapr)

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
    adctemplib = tech+'_adc_sar_templates'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.load_template(filename=adctemplib+'.yaml', libname=adctemplib)
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
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    mycell_list = []
    #capdrv generation
    cellname='sarfsm'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarfsm(laygen, objectname_pfix='FSM0', templib_logic=logictemplib, placement_grid=pg,
                    routing_grid_m3m4=rg_m3m4, num_bits=8, m=1, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0]))
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
