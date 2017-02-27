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


def generate_sarclkdelayslice(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                       m=2, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    inv_name = 'inv_' + str(m) + 'x'
    nand_name = 'nand_' + str(m) + 'x'
    mux_name = 'mux2to1_' + str(m) + 'x'

    # placement
    isel0 = laygen.place(name="I" + objectname_pfix + 'INVSEL0', templatename=inv_name,
                         gridname=pg, xy=origin, template_libname=templib_logic)
    inand0 = laygen.relplace(name="I" + objectname_pfix + 'ND0', templatename=nand_name,
                             gridname=pg, refinstname=isel0.name, template_libname=templib_logic)
    iinv00 = laygen.relplace(name="I" + objectname_pfix + 'INV00', templatename=inv_name,
                            gridname=pg, refinstname=inand0.name, template_libname=templib_logic)
    inand1 = laygen.relplace(name="I" + objectname_pfix + 'ND1', templatename=nand_name,
                             gridname=pg, refinstname=iinv00.name, template_libname=templib_logic)
    iinv10 = laygen.relplace(name="I" + objectname_pfix + 'INV10', templatename=inv_name,
                             gridname=pg, refinstname=inand1.name, template_libname=templib_logic)
    iinv11 = laygen.relplace(name="I" + objectname_pfix + 'INV11', templatename=inv_name,
                             gridname=pg, refinstname=iinv10.name, template_libname=templib_logic)
    iinv12 = laygen.relplace(name="I" + objectname_pfix + 'INV12', templatename=inv_name,
                             gridname=pg, refinstname=iinv11.name, template_libname=templib_logic)
    imux0 = laygen.relplace(name="I" + objectname_pfix + 'MUX0', templatename=mux_name,
                            gridname=pg, refinstname=iinv12.name, template_libname=templib_logic)

    # internal pins
    pdict = laygen.get_inst_pin_coord(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=isel0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=imux0.name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=imux0.cellname, gridname=rg_m3m4, libname=templib_logic)[0] - 1
    y0 = pdict[isel0.name]['I'][0][1] + 0

    #route-sel
    [rv0, rsel0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['I'][0],
                                       pdict[inand1.name]['B'][0], y0, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['I'][0],
                                       pdict[imux0.name]['EN1'][0], y0, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['O'][0],
                                       pdict[inand0.name]['B'][0], y0+1, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['O'][0],
                                       pdict[imux0.name]['EN0'][0], y0+1, rg_m3m4)
    #route-input
    rv0, rin0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand0.name]['A'][0],
                                np.array([x0, y0+2]), rg_m3m4)
    rv0, rin1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand1.name]['A'][0],
                                np.array([x0, y0+2]), rg_m3m4)
    #route-path0
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand0.name]['O'][0],
                                       pdict[iinv00.name]['I'][0], y0+3, rg_m3m4, extendl=2, extendr=2)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv00.name]['O'][0],
                                       pdict[imux0.name]['I0'][0], y0+4, rg_m3m4)
    #route-path1
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand1.name]['O'][0],
                                       pdict[iinv10.name]['I'][0], y0+3, rg_m3m4, extendl=2, extendr=2)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv10.name]['O'][0],
                                       pdict[iinv11.name]['I'][0], y0+2, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv11.name]['O'][0],
                                       pdict[iinv12.name]['I'][0], y0+3, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv12.name]['O'][0],
                                       pdict[imux0.name]['I1'][0], y0+5, rg_m3m4)
    #route-output
    rv0, rout0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['O'][0],
                                np.array([x1, y0+2]), rg_m3m4)

    #pins
    laygen.create_boundary_pin_form_rect(rin0, rg_m3m4, "I", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rsel0, rg_m3m4, "SEL", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rout0, rg_m3m4, "O", laygen.layers['pin'][4], size=6, direction='right')

    # power pin
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=isel0, inst_right=imux0)

def generate_sarclkdelayslice_compact(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                       m=2, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    inv_name = 'inv_' + str(m) + 'x'
    mux_name = 'mux2to1_' + str(m) + 'x'

    # placement
    isel0 = laygen.place(name="I" + objectname_pfix + 'INVSEL0', templatename=inv_name,
                         gridname=pg, xy=origin, template_libname=templib_logic)
    iinv11 = laygen.relplace(name="I" + objectname_pfix + 'INV11', templatename=inv_name,
                             gridname=pg, refinstname=isel0.name, template_libname=templib_logic)
    iinv12 = laygen.relplace(name="I" + objectname_pfix + 'INV12', templatename=inv_name,
                             gridname=pg, refinstname=iinv11.name, template_libname=templib_logic)
    imux0 = laygen.relplace(name="I" + objectname_pfix + 'MUX0', templatename=mux_name,
                            gridname=pg, refinstname=iinv12.name, template_libname=templib_logic)

    # internal pins
    pdict = laygen.get_inst_pin_coord(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=isel0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=imux0.name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=imux0.cellname, gridname=rg_m3m4, libname=templib_logic)[0] - 1
    y0 = pdict[isel0.name]['I'][0][1] + 0

    #route-sel
    [rv0, rsel0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['I'][0],
                                       pdict[imux0.name]['EN1'][0], y0, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['O'][0],
                                       pdict[imux0.name]['EN0'][0], y0+1, rg_m3m4)
    #route-input
    #rv0, rin0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['I0'][0],
    #                            np.array([x0, y0+2]), rg_m3m4)
    #rv0, rin1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv11.name]['I'][0],
    #                            np.array([x0, y0+2]), rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv11.name]['I'][0],
                                       pdict[imux0.name]['I0'][0], y0+2, rg_m3m4)
    #route-path1
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv11.name]['O'][0],
                                       pdict[iinv12.name]['I'][0], y0+3, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv12.name]['O'][0],
                                       pdict[imux0.name]['I1'][0], y0+5, rg_m3m4)
    #route-output
    rv0, rout0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['O'][0],
                                np.array([x1, y0+2]), rg_m3m4)

    #pins
    laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=pdict[iinv11.name]['I'], gridname=rg_m3m4)
    #laygen.create_boundary_pin_form_rect(rin0, rg_m3m4, "I", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rsel0, rg_m3m4, "SEL", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rout0, rg_m3m4, "O", laygen.layers['pin'][4], size=6, direction='right')

    # power pin
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=isel0, inst_right=imux0)

def generate_sarclkdelayslice_compact_2x(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                       m=2, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    inv_name = 'inv_' + str(m) + 'x'
    mux_name = 'mux2to1_' + str(m) + 'x'

    # placement
    isel0 = laygen.place(name="I" + objectname_pfix + 'INVSEL0', templatename=inv_name,
                         gridname=pg, xy=origin, template_libname=templib_logic)
    iinv11 = laygen.relplace(name="I" + objectname_pfix + 'INV11', templatename=inv_name,
                             gridname=pg, refinstname=isel0.name, template_libname=templib_logic)
    iinv12 = laygen.relplace(name="I" + objectname_pfix + 'INV12', templatename=inv_name,
                             gridname=pg, refinstname=iinv11.name, template_libname=templib_logic)
    iinv13 = laygen.relplace(name="I" + objectname_pfix + 'INV13', templatename=inv_name,
                             gridname=pg, refinstname=iinv12.name, template_libname=templib_logic)
    iinv14 = laygen.relplace(name="I" + objectname_pfix + 'INV14', templatename=inv_name,
                             gridname=pg, refinstname=iinv13.name, template_libname=templib_logic)
    imux0 = laygen.relplace(name="I" + objectname_pfix + 'MUX0', templatename=mux_name,
                            gridname=pg, refinstname=iinv14.name, template_libname=templib_logic)

    # internal pins
    pdict = laygen.get_inst_pin_coord(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=isel0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=imux0.name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=imux0.cellname, gridname=rg_m3m4, libname=templib_logic)[0] - 1
    y0 = pdict[isel0.name]['I'][0][1] + 0

    #route-sel
    [rv0, rsel0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['I'][0],
                                       pdict[imux0.name]['EN1'][0], y0, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['O'][0],
                                       pdict[imux0.name]['EN0'][0], y0+1, rg_m3m4)
    #route-input
    rv0, rin0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['I0'][0],
                                np.array([x0, y0+2]), rg_m3m4)
    rv0, rin1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv11.name]['I'][0],
                                np.array([x0, y0+2]), rg_m3m4)
    #route-path1
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv11.name]['O'][0],
                                       pdict[iinv12.name]['I'][0], y0+3, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv12.name]['O'][0],
                                       pdict[iinv13.name]['I'][0], y0+5, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv13.name]['O'][0],
                                       pdict[iinv14.name]['I'][0], y0+3, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv14.name]['O'][0],
                                       pdict[imux0.name]['I1'][0], y0+5, rg_m3m4)
    #route-output
    #rv0, rout0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['O'][0],
    #                            np.array([x1, y0+2]), rg_m3m4)

    #pins
    laygen.create_boundary_pin_form_rect(rin0, rg_m3m4, "I", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rsel0, rg_m3m4, "SEL", laygen.layers['pin'][4], size=6, direction='left')
  
    laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=pdict[imux0.name]['O'], gridname=rg_m3m4)

    # power pin
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=isel0, inst_right=imux0)

def generate_sarclkdelay(laygen, objectname_pfix, templib_logic, workinglib, placement_grid, routing_grid_m3m4,
                         m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    slice_name = 'sarclkdelayslice'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    islice3 = laygen.relplace(name="I" + objectname_pfix + 'SL3', templatename=slice_name,
                              gridname=pg, refinstname=itapl.name, template_libname=workinglib, transform='MY')
    islice2 = laygen.relplace(name="I" + objectname_pfix + 'SL2', templatename=slice_name,
                              gridname=pg, refinstname=islice3.name, template_libname=workinglib, transform='MY')
    islice1 = laygen.relplace(name="I" + objectname_pfix + 'SK1', templatename=slice_name,
                              gridname=pg, refinstname=islice2.name, template_libname=workinglib, transform='MY')
    islice0 = laygen.relplace(name="I" + objectname_pfix + 'SL0', templatename=slice_name,
                              gridname=pg, refinstname=islice1.name, template_libname=workinglib, transform='MY')
    isp4x = []
    isp2x = []
    isp1x = []
    refi=islice0.name
    if not m_space_4x==0:
        isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X0', templatename=space_4x_name,
                     shape = np.array([m_space_4x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp4x[-1].name
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
    itapr=laygen.relplace(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                          gridname = pg, refinstname = refi, template_libname = templib_logic)

    # internal pins
    pdict = laygen.get_inst_pin_coord(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=islice0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=islice3.name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=islice3.cellname, gridname=rg_m3m4, libname=workinglib)[0] - 1
    y0 = pdict[islice0.name]['I'][0][1] + 0

    #route-backtoback
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islice0.name, refpinname0='O', refinstname1=islice1.name, refpinname1='I')
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islice1.name, refpinname0='O', refinstname1=islice2.name, refpinname1='I')
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islice2.name, refpinname0='O', refinstname1=islice3.name, refpinname1='I')

    #route-sel
    rsel0 = laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([x0, y0-2]), gridname0=rg_m3m4,
                         refinstname0=islice0.name, refpinname0='SEL')
    rv0, rsel1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice1.name]['SEL'][0],
                                   np.array([x0, y0-4]), rg_m3m4)
    rv0, rsel2 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice2.name]['SEL'][0],
                                   np.array([x0, y0-5]), rg_m3m4)
    rv0, rsel3 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice3.name]['SEL'][0],
                                   np.array([x0, y0-6]), rg_m3m4)

    #pins
    laygen.pin(name='I', layer=laygen.layers['pin'][4], xy=pdict[islice0.name]['I'], gridname=rg_m3m4)
    laygen.create_boundary_pin_form_rect(rsel0, rg_m3m4, "SEL<0>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel1, rg_m3m4, "SEL<1>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel2, rg_m3m4, "SEL<2>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel3, rg_m3m4, "SEL<3>", laygen.layers['pin'][4], size=6, direction='right')
    #[rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][3],
    #                                   pdict[islice3.name]['O'][0], np.array([x0, pdict[islice3.name]['O'][1][1]-3]),
    #                                   pdict[islice3.name]['O'][1][0], rg_m3m4)
    #laygen.create_boundary_pin_form_rect(rh1, rg_m3m4, "O", laygen.layers['pin'][4], size=6, direction='left')
    laygen.pin(name='O', layer=laygen.layers['pin'][4], xy=pdict[islice3.name]['O'], gridname=rg_m3m4)



    # power pin
    #create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=itapl, inst_right=itapr)

    # power pin
    pwr_dim=laygen.get_template_size(name=itapl.cellname, gridname=rg_m2m3, libname=itapl.libname)
    rvdd = []
    rvss = []
    rp1='VDD'
    for i in range(1, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-2), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-2), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-1), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-1), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
    for j in range(1, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))

def generate_sarclkdelay_compact(laygen, objectname_pfix, templib_logic, workinglib, placement_grid, routing_grid_m3m4,
                         m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    slice_name = 'sarclkdelayslice_compact'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    islice3 = laygen.relplace(name="I" + objectname_pfix + 'SL3', templatename=slice_name,
                              gridname=pg, refinstname=itapl.name, template_libname=workinglib, transform='MY')
    islice2 = laygen.relplace(name="I" + objectname_pfix + 'SL2', templatename=slice_name,
                              gridname=pg, refinstname=islice3.name, template_libname=workinglib, transform='MY')
    islice1 = laygen.relplace(name="I" + objectname_pfix + 'SK1', templatename=slice_name,
                              gridname=pg, refinstname=islice2.name, template_libname=workinglib, transform='MY')
    islice0 = laygen.relplace(name="I" + objectname_pfix + 'SL0', templatename=slice_name,
                              gridname=pg, refinstname=islice1.name, template_libname=workinglib, transform='MY')
    isp4x = []
    isp2x = []
    isp1x = []
    refi=islice0.name
    if not m_space_4x==0:
        isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X0', templatename=space_4x_name,
                     shape = np.array([m_space_4x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp4x[-1].name
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
    itapr=laygen.relplace(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                          gridname = pg, refinstname = refi, template_libname = templib_logic)

    # internal pins
    pdict = laygen.get_inst_pin_coord(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=islice0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=islice3.name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=islice3.cellname, gridname=rg_m3m4, libname=workinglib)[0] - 1
    y0 = pdict[islice0.name]['I'][0][1] + 0

    #route-backtoback
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islice0.name, refpinname0='O', refinstname1=islice1.name, refpinname1='I')
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islice1.name, refpinname0='O', refinstname1=islice2.name, refpinname1='I')
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islice2.name, refpinname0='O', refinstname1=islice3.name, refpinname1='I')

    #route-sel
    rsel0 = laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([x0, y0-2]), gridname0=rg_m3m4,
                         refinstname0=islice0.name, refpinname0='SEL')
    rv0, rsel1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice1.name]['SEL'][0],
                                   np.array([x0, y0-4]), rg_m3m4)
    rv0, rsel2 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice2.name]['SEL'][0],
                                   np.array([x0, y0-5]), rg_m3m4)
    rv0, rsel3 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice3.name]['SEL'][0],
                                   np.array([x0, y0-6]), rg_m3m4)

    #pins
    laygen.pin(name='I', layer=laygen.layers['pin'][4], xy=pdict[islice0.name]['I'], gridname=rg_m3m4)
    laygen.create_boundary_pin_form_rect(rsel0, rg_m3m4, "SEL<0>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel1, rg_m3m4, "SEL<1>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel2, rg_m3m4, "SEL<2>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel3, rg_m3m4, "SEL<3>", laygen.layers['pin'][4], size=6, direction='right')
    #[rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][3],
    #                                   pdict[islice3.name]['O'][0], np.array([x0, pdict[islice3.name]['O'][1][1]-3]),
    #                                   pdict[islice3.name]['O'][1][0], rg_m3m4)
    #laygen.create_boundary_pin_form_rect(rh1, rg_m3m4, "O", laygen.layers['pin'][4], size=6, direction='left')
    laygen.pin(name='O', layer=laygen.layers['pin'][4], xy=pdict[islice3.name]['O'], gridname=rg_m3m4)



    # power pin
    #create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=itapl, inst_right=itapr)

    # power pin
    pwr_dim=laygen.get_template_size(name=itapl.cellname, gridname=rg_m2m3, libname=itapl.libname)
    rvdd = []
    rvss = []
    rp1='VDD'
    for i in range(1, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-2), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-2), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-1), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-1), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
    for j in range(1, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))

def generate_sarclkdelay_compact_dual(laygen, objectname_pfix, templib_logic, workinglib, placement_grid, routing_grid_m3m4,
                         m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    tie_name = 'tie_2x'
    dff_name = 'dff_rsth_1x'
    inv_name = 'inv_1x'
    mux_name = 'mux2to1_1x'
    slice_name = 'sarclkdelayslice_compact'
    slice_2x_name = 'sarclkdelayslice_compact_2x'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    imux0 = laygen.relplace(name="I" + objectname_pfix + 'MUX0', templatename=mux_name,
                              gridname=pg, refinstname=itapl.name, template_libname=templib_logic, transform='MY')
    iinv0 = laygen.relplace(name="I" + objectname_pfix + 'INV0', templatename=inv_name,
                              gridname=pg, refinstname=imux0.name, template_libname=templib_logic, transform='MY')
    idff0 = laygen.relplace(name="I" + objectname_pfix + 'DFF0', templatename=dff_name,
                              gridname=pg, refinstname=iinv0.name, template_libname=templib_logic, transform='MY')
    itie0 = laygen.relplace(name="I" + objectname_pfix + 'TIE0', templatename=tie_name,
                              gridname=pg, refinstname=idff0.name, template_libname=templib_logic, transform='MY')
    islice11 = laygen.relplace(name="I" + objectname_pfix + 'SL11', templatename=slice_2x_name,
                              gridname=pg, refinstname=itie0.name, template_libname=workinglib, transform='MY')
    islice10 = laygen.relplace(name="I" + objectname_pfix + 'SL10', templatename=slice_name,
                              gridname=pg, refinstname=islice11.name, template_libname=workinglib, transform='MY')
    islice01 = laygen.relplace(name="I" + objectname_pfix + 'SL01', templatename=slice_2x_name,
                              gridname=pg, refinstname=islice10.name, template_libname=workinglib, transform='MY')
    islice00 = laygen.relplace(name="I" + objectname_pfix + 'SL00', templatename=slice_name,
                              gridname=pg, refinstname=islice01.name, template_libname=workinglib, transform='MY')


    isp4x = []
    isp2x = []
    isp1x = []
    refi=islice00.name
    if not m_space_4x==0:
        isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X0', templatename=space_4x_name,
                     shape = np.array([m_space_4x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp4x[-1].name
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
    itapr=laygen.relplace(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                          gridname = pg, refinstname = refi, template_libname = templib_logic)

    # internal pins
    pdict = laygen.get_inst_pin_coord(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=islice00.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=imux0.name, gridname=rg_m3m4)[0]\
         -laygen.get_template_size(name=imux0.cellname, gridname=rg_m3m4, libname=templib_logic)[0] - 1 + 2
    #x1 = laygen.get_inst_xy(name=islice11.name, gridname=rg_m3m4)[0]\
    #     +laygen.get_template_size(name=islice11.cellname, gridname=rg_m3m4, libname=workinglib)[0] - 1
    y0 = pdict[islice00.name]['I'][0][1] + 2

    #route-backtoback
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islice00.name, refpinname0='O', refinstname1=islice01.name, refpinname1='I')
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islice10.name, refpinname0='O', refinstname1=islice11.name, refpinname1='I')

    #route-sel
    rv0, rsel00 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice00.name]['SEL'][0],
                                   np.array([x0, y0-2]), rg_m3m4)
    rv0, rsel01 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice01.name]['SEL'][0],
                                   np.array([x0, y0+2]), rg_m3m4)
    rv0, rsel10 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice10.name]['SEL'][0],
                                   np.array([x0, y0-4]), rg_m3m4)
    rv0, rsel11 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice11.name]['SEL'][0],
                                   np.array([x0, y0-5]), rg_m3m4)

    #route-tie
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[itie0.name]['TIEVSS'][0],
                                         pdict[idff0.name]['I'][0], y0-2, rg_m3m4)
    #route-en1
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['I'][0],
                                         pdict[idff0.name]['O'][0], y0-5, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['EN1'][0],
                                         pdict[idff0.name]['O'][0], y0-5, rg_m3m4)
    #route-en0
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['O'][0],
                                         pdict[imux0.name]['EN0'][0], y0-3, rg_m3m4)
    #route-o0
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice01.name]['O'][0],
                                         pdict[imux0.name]['I0'][0], y0+2, rg_m3m4)
    #route-o1
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice11.name]['O'][0],
                                         pdict[imux0.name]['I1'][0], y0+1, rg_m3m4)
    #route-rst
    rv0, rrst0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[idff0.name]['RST'][0],
                                   np.array([x1, y0+3]), rg_m3m4)
    #route-sb
    rv0, rsb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[idff0.name]['CLK'][0],
                                   np.array([x1, y0+4-4]), rg_m3m4)
    #route-out
    rv0, ro0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['O'][0],
                                   np.array([x1, y0-2]), rg_m3m4)
    #route-input
    rv0, ri0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice00.name]['I'][0],
                                   np.array([x0, y0-3]), rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice00.name]['I'][0],
                                         pdict[islice10.name]['I'][0], y0-3, rg_m3m4)

    #pins
    #laygen.pin(name='I', layer=laygen.layers['pin'][4], xy=pdict[islice00.name]['I'], gridname=rg_m3m4)
    laygen.create_boundary_pin_form_rect(ri0, rg_m3m4, "I", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel00, rg_m3m4, "SEL0<0>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel01, rg_m3m4, "SEL0<1>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel10, rg_m3m4, "SEL1<0>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rsel11, rg_m3m4, "SEL1<1>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rrst0, rg_m3m4, "RST", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rsb0, rg_m3m4, "SB", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(ro0, rg_m3m4, "O", laygen.layers['pin'][4], size=6, direction='left')

    # power pin
    pwr_dim=laygen.get_template_size(name=itapl.cellname, gridname=rg_m2m3, libname=itapl.libname)
    rvdd = []
    rvss = []
    rp1='VDD'
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-2), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-2), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-1), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-1), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
    for j in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))


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
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    mycell_list = []
    num_bits=9
    #load from preset
    load_from_file=True
    yamlfile_system_input="adc_sar_dsn_system_input.yaml"
    if load_from_file==True:
        with open(yamlfile_system_input, 'r') as stream:
            sysdict_i = yaml.load(stream)
        num_bits=sysdict_i['n_bit']
    #cell generation (slice)
    cellname='sarclkdelayslice'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelayslice(laygen, objectname_pfix='DSL0', templib_logic=logictemplib, placement_grid=pg,
                               routing_grid_m3m4=rg_m3m4, m=1, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    # array generation (2 step)
    cellname='sarclkdelay'
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelay(laygen, objectname_pfix='CKD0', templib_logic=logictemplib, workinglib=workinglib,
                         placement_grid=pg, routing_grid_m3m4=rg_m3m4, m_space_4x=0, m_space_2x=0, m_space_1x=0,
                         origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw_'+str(num_bits-1)+'b', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]  \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x=int(m_space/4)
    m_space_2x=int((m_space-m_space_4x*4)/2)
    m_space_1x=int(m_space-m_space_4x*4-m_space_2x*2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelay(laygen, objectname_pfix='CKD0', templib_logic=logictemplib, workinglib=workinglib,
                         placement_grid=pg, routing_grid_m3m4=rg_m3m4, m_space_4x=m_space_4x, m_space_2x=m_space_2x,
                         m_space_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    #cell generation (slice_compact)
    cellname='sarclkdelayslice_compact'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelayslice_compact(laygen, objectname_pfix='DSL0', templib_logic=logictemplib, placement_grid=pg,
                               routing_grid_m3m4=rg_m3m4, m=1, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    cellname='sarclkdelayslice_compact_2x'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelayslice_compact_2x(laygen, objectname_pfix='DSL0', templib_logic=logictemplib, placement_grid=pg,
                               routing_grid_m3m4=rg_m3m4, m=1, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #array generation (2 step)
    cellname='sarclkdelay_compact'
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelay_compact(laygen, objectname_pfix='CKD0', templib_logic=logictemplib, workinglib=workinglib,
                         placement_grid=pg, routing_grid_m3m4=rg_m3m4, m_space_4x=0, m_space_2x=0, m_space_1x=0,
                         origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw_'+str(num_bits-1)+'b', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]  \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x=int(m_space/4)
    m_space_2x=int((m_space-m_space_4x*4)/2)
    m_space_1x=int(m_space-m_space_4x*4-m_space_2x*2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelay_compact(laygen, objectname_pfix='CKD0', templib_logic=logictemplib, workinglib=workinglib,
                         placement_grid=pg, routing_grid_m3m4=rg_m3m4, m_space_4x=m_space_4x, m_space_2x=m_space_2x,
                         m_space_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    # dual_array generation (2 step)
    cellname='sarclkdelay_compact_dual'
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelay_compact_dual(laygen, objectname_pfix='CKD0', templib_logic=logictemplib, workinglib=workinglib,
                         placement_grid=pg, routing_grid_m3m4=rg_m3m4, m_space_4x=0, m_space_2x=0, m_space_1x=0,
                         origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw_'+str(num_bits-1)+'b', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]  \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x=int(m_space/4)
    m_space_2x=int((m_space-m_space_4x*4)/2)
    m_space_1x=int(m_space-m_space_4x*4-m_space_2x*2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelay_compact_dual(laygen, objectname_pfix='CKD0', templib_logic=logictemplib, workinglib=workinglib,
                         placement_grid=pg, routing_grid_m3m4=rg_m3m4, m_space_4x=m_space_4x, m_space_2x=m_space_2x,
                         m_space_1x=m_space_1x, origin=np.array([0, 0]))
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
