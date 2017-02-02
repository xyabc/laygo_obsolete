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


def generate_sarafe(laygen, objectname_pfix, workinglib, placement_grid,
                    routing_grid_m2m3_thick, routing_grid_m3m4_thick,
                    routing_grid_m5m6, routing_grid_m6m7,
                    num_bits=8, num_bits_vertical=5, m_sa=8, origin=np.array([0, 0])):
    """generate sar analog frontend """
    pg = placement_grid

    rg_m3m4_thick = routing_grid_m3m4_thick
    rg_m5m6 = routing_grid_m5m6
    rg_m6m7 = routing_grid_m6m7

    tap_name='tap'
    cdrv_name='capdrv_array_'+str(num_bits-1)+'b'
    cdac_name='capdac_'+str(num_bits-1)+'b'
    sa_name='salatch_pmos'
    space_1x_name='space_1x'

    # placement
    #laygen.get_template_size(templatename, gridname, libname=template_libname)

    # laygen.get_template_size(cdac_name, gridname=pg, libname=workinglib)
    # laygen.get_template_size(cdac_name, gridname=pg, libname=workinglib)
    xy0 = origin + (laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib)*np.array([1, 0]) )
    icdrvl = laygen.place(name="I" + objectname_pfix + 'CDRVL0', templatename=cdrv_name, gridname=pg,
                          xy=xy0, template_libname = workinglib, transform='MY')
    icdrvr = laygen.place(name="I" + objectname_pfix + 'CDRVR0', templatename=cdrv_name, gridname=pg,
                          xy=xy0, template_libname = workinglib)
    xy0 = origin + laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib)*np.array([0, 1]) \
                 + laygen.get_template_size(sa_name, gridname=pg, libname=workinglib) * np.array([0, 1])
    isa = laygen.place(name="I" + objectname_pfix + 'SA0', templatename=sa_name, gridname=pg,
                       xy=xy0, template_libname = workinglib, transform='MX')
    xy0 = origin + laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib)*np.array([0, 1]) \
                 + laygen.get_template_size(sa_name, gridname=pg, libname=workinglib) * np.array([0, 1]) \
                 + laygen.get_template_size(cdac_name, gridname=pg, libname=workinglib)*np.array([1, 0])
    icdacl = laygen.place(name="I" + objectname_pfix + 'CDACL0', templatename=cdac_name, gridname=pg,
                          xy=xy0, template_libname = workinglib, transform='MY')
    xy0 = origin + laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib)*np.array([2, 1]) \
                 + laygen.get_template_size(sa_name, gridname=pg, libname=workinglib) * np.array([0, 1]) \
                 - laygen.get_template_size(cdac_name, gridname=pg, libname=workinglib)*np.array([1, 0])
    icdacr = laygen.place(name="I" + objectname_pfix + 'CDACR0', templatename=cdac_name, gridname=pg,
                          xy=xy0, template_libname = workinglib)

    # internal pins
    icdrvl_vo_xy = []
    icdacl_i_xy = []
    icdrvr_vo_xy = []
    icdacr_i_xy = []

    icdrvl_vo_c0_xy = laygen.get_inst_pin_coord(icdrvl.name, 'VO_C0', rg_m5m6)
    icdacl_i_c0_xy = laygen.get_inst_pin_coord(icdacl.name, 'I_C0', rg_m5m6)
    icdrvr_vo_c0_xy = laygen.get_inst_pin_coord(icdrvr.name, 'VO_C0', rg_m5m6)
    icdacr_i_c0_xy = laygen.get_inst_pin_coord(icdacr.name, 'I_C0', rg_m5m6)
    for i in range(num_bits-1):
        icdrvl_vo_xy.append(laygen.get_inst_pin_coord(icdrvl.name, 'VO<' + str(i) + '>', rg_m5m6))
        icdacl_i_xy.append(laygen.get_inst_pin_coord(icdacl.name, 'I<' + str(i) + '>', rg_m5m6))
        icdrvr_vo_xy.append(laygen.get_inst_pin_coord(icdrvr.name, 'VO<' + str(i) + '>', rg_m5m6))
        icdacr_i_xy.append(laygen.get_inst_pin_coord(icdacr.name, 'I<' + str(i) + '>', rg_m5m6))

    #route
    #capdrv to capdac
    y0 = origin[1] + laygen.get_template_size(cdrv_name, gridname=rg_m5m6, libname=workinglib)[1]-2
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6], icdrvl_vo_c0_xy[0],
                                       icdacl_i_c0_xy[0], y0 + 2, rg_m5m6, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7)
    laygen.create_boundary_pin_form_rect(rv0, rg_m5m6, "VOL_C0", laygen.layers['pin'][5], size=4, direction='bottom', netname='VREF<1>')
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6], icdrvr_vo_c0_xy[0],
                                       icdacr_i_c0_xy[0], y0 + 2, rg_m5m6, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7)
    laygen.create_boundary_pin_form_rect(rv0, rg_m5m6, "VOR_C0", laygen.layers['pin'][5], size=4, direction='bottom', netname='VREF<1>')

    for i in range(num_bits-1):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6], icdrvl_vo_xy[i][0],
                                           icdacl_i_xy[i][0], y0 - i, rg_m5m6, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7)
        laygen.create_boundary_pin_form_rect(rv0, rg_m5m6, "VOL<"+str(i)+">", laygen.layers['pin'][5], size=4, direction='bottom')
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6], icdrvr_vo_xy[i][0],
                                           icdacr_i_xy[i][0], y0 - i, rg_m5m6, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7)
        laygen.create_boundary_pin_form_rect(rv0, rg_m5m6, "VOR<"+str(i)+">", laygen.layers['pin'][5], size=4, direction='bottom')


    #vref
    rvref0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                        refinstname0=icdrvl.name, refpinname0='VREF<0>', gridname0=rg_m4m5,
                        refinstname1=icdrvr.name, refpinname1='VREF<0>')
    rvref1=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                        refinstname0=icdrvl.name, refpinname0='VREF<1>', gridname0=rg_m4m5,
                        refinstname1=icdrvr.name, refpinname1='VREF<1>')
    rvref2=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                        refinstname0=icdrvl.name, refpinname0='VREF<2>', gridname0=rg_m4m5,
                        refinstname1=icdrvr.name, refpinname1='VREF<2>')
    #input pins
    #y0 = laygen.get_inst_pin_coord(icdrvl.name, 'EN0<0>', rg_m4m5, index=np.array([0, 0]), sort=True)[0][1]
    y0 = 0
    rclkb=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                      refinstname0=isa.name, refpinname0='CLKB', gridname0=rg_m4m5, direction='y')
    routp=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                      refinstname0=isa.name, refpinname0='OUTP', gridname0=rg_m4m5, direction='y')
    routm=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                      refinstname0=isa.name, refpinname0='OUTM', gridname0=rg_m4m5, direction='y')
    rosp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                      refinstname0=isa.name, refpinname0='OSP', gridname0=rg_m2m3, direction='y')
    rosm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                      refinstname0=isa.name, refpinname0='OSM', gridname0=rg_m2m3, direction='y')
    renl0 = []
    renl1 = []
    renl2 = []
    renr0 = []
    renr1 = []
    renr2 = []
    for i in range(num_bits-1):
        renl0.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvl.name, refpinname0='EN'+str(i)+'<0>', gridname0=rg_m5m6, direction='y'))
        renl1.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvl.name, refpinname0='EN'+str(i)+'<1>', gridname0=rg_m5m6, direction='y'))
        renl2.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvl.name, refpinname0='EN'+str(i)+'<2>', gridname0=rg_m5m6, direction='y'))
        renr0.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvr.name, refpinname0='EN'+str(i)+'<0>', gridname0=rg_m5m6, direction='y'))
        renr1.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvr.name, refpinname0='EN'+str(i)+'<1>', gridname0=rg_m5m6, direction='y'))
        renr2.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvr.name, refpinname0='EN'+str(i)+'<2>', gridname0=rg_m5m6, direction='y'))
    #inp/inm
    num_bits_cdaco=2**(num_bits_vertical-1)-1
    x0 = laygen.get_inst_xy(icdacl.name, rg_m5m6)[0] - 2
    x1 = laygen.get_inst_xy(icdacr.name, rg_m5m6)[0] + 2
    for i in range(num_bits_cdaco):
        xy0=laygen.get_inst_pin_coord(icdacl.name, "O"+str(i), rg_m5m6, index=np.array([0, 0]), sort=True)[0]
        rinp = laygen.route(None, laygen.layers['metal'][6], xy0=xy0, xy1=np.array([x0, xy0[1]]), gridname0=rg_m5m6)
        for j in range(4):
            laygen.via(None, [x0-2*j, xy0[1]], rg_m5m6)
        xy0=laygen.get_inst_pin_coord(icdacr.name, "O"+str(i), rg_m5m6, index=np.array([0, 0]), sort=True)[1]
        rinm = laygen.route(None, laygen.layers['metal'][6], xy0=xy0, xy1=np.array([x1, xy0[1]]), gridname0=rg_m5m6)
        for j in range(4):
            laygen.via(None, [x1+2*j, xy0[1]], rg_m5m6)
    #xy0 = laygen.get_inst_pin_coord(icdacl.name, "O0", rg_m5m6, index=np.array([0, 0]), sort=True)[0]
    xy0 = laygen.get_inst_pin_coord(isa.name, "INP", rg_m3m4, index=np.array([0, 0]), sort=True)[0]
    xy1 = laygen.get_inst_pin_coord(icdacl.name, "O"+str(num_bits_cdaco-1), rg_m5m6, index=np.array([0, 0]), sort=True)[0]
    for j in range(4):
        laygen.route(None, laygen.layers['metal'][5], xy0=np.array([x0-2*j, xy0[1]]), xy1=np.array([x0-2*j, xy1[1]]), gridname0=rg_m5m6)
    #xy0 = laygen.get_inst_pin_coord(icdacr.name, "O0", rg_m5m6, index=np.array([0, 0]), sort=True)[0]
    xy0 = laygen.get_inst_pin_coord(isa.name, "INM", rg_m4m5, index=np.array([0, 0]), sort=True)[0]
    xy1 = laygen.get_inst_pin_coord(icdacr.name, "O"+str(num_bits_cdaco-1), rg_m5m6, index=np.array([0, 0]), sort=True)[0]
    for j in range(4):
        laygen.route(None, laygen.layers['metal'][5], xy0=np.array([x1+2*j, xy0[1]]), xy1=np.array([x1+2*j, xy1[1]]), gridname0=rg_m5m6)
    #inp/inm - sa to capdac
    xy0 = laygen.get_inst_pin_coord(isa.name, "INP", rg_m4m5, index=np.array([0, 0]), sort=True)[0]
    xy1 = laygen.get_inst_pin_coord(isa.name, "INM", rg_m4m5, index=np.array([0, 0]), sort=True)[0]
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0-6, xy0[1]]), xy1=xy0, gridname0=rg_m4m5)
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x1+6, xy1[1]]), xy1=xy1, gridname0=rg_m4m5)
    for j in range(4):
        laygen.via(None, [x0 - 2 * j, xy0[1]], rg_m4m5)
        laygen.via(None, [x1 + 2 * j, xy1[1]], rg_m4m5)
    x0 = laygen.get_inst_xy(icdacl.name, rg_m3m4)[0] - 1
    x1 = laygen.get_inst_xy(icdacr.name, rg_m3m4)[0] + 1
    xy0 = laygen.get_inst_pin_coord(isa.name, "INP", rg_m3m4, index=np.array([0, 0]), sort=True)[0]
    xy1 = laygen.get_inst_pin_coord(isa.name, "INM", rg_m3m4, index=np.array([0, 0]), sort=True)[0]
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0, xy0[1]]), xy1=xy0, gridname0=rg_m3m4, addvia1=True)
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x1, xy1[1]]), xy1=xy1, gridname0=rg_m3m4, addvia1=True)

    #vdd/vss - capdrv
    y0 = laygen.get_inst_xy(icdrvl.name, rg_m3m4_thick)[1] \
         + laygen.get_template_size(icdrvl.cellname, rg_m3m4_thick, libname=workinglib)[1]\
         - laygen.get_template_size('boundary_top', rg_m3m4_thick)[1] + 1
    x0 = 0
    x1 = laygen.get_inst_xy(icdrvr.name, rg_m3m4_thick)[0] \
         + laygen.get_template_size(icdrvr.cellname, rg_m3m4_thick, libname=workinglib)[0]

    rvdd0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0, y0]), xy1=np.array([x1, y0]), gridname0=rg_m3m4_thick)
    rvss0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0, y0+1]), xy1=np.array([x1, y0+1]), gridname0=rg_m3m4_thick)
    rvdd1=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0, y0+2]), xy1=np.array([x1, y0+2]), gridname0=rg_m3m4_thick)
    rvss1=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0, y0+3]), xy1=np.array([x1, y0+3]), gridname0=rg_m3m4_thick)

    rvss0_pin_xy = laygen.get_rect_xy(rvss0.name, rg_m3m4_thick)
    rvss1_pin_xy = laygen.get_rect_xy(rvss1.name, rg_m3m4_thick)
    rvdd0_pin_xy = laygen.get_rect_xy(rvdd0.name, rg_m3m4_thick)
    rvdd1_pin_xy = laygen.get_rect_xy(rvdd1.name, rg_m3m4_thick)

    #vdd horizontal pins
    laygen.pin(name='VSS0', layer=laygen.layers['pin'][4], xy=rvss0_pin_xy, gridname=rg_m3m4_thick, netname='VSS')
    laygen.pin(name='VSS1', layer=laygen.layers['pin'][4], xy=rvss1_pin_xy, gridname=rg_m3m4_thick, netname='VSS')
    laygen.pin(name='VDD0', layer=laygen.layers['pin'][4], xy=rvdd0_pin_xy, gridname=rg_m3m4_thick, netname='VDD')
    laygen.pin(name='VDD1', layer=laygen.layers['pin'][4], xy=rvdd1_pin_xy, gridname=rg_m3m4_thick, netname='VDD')


    t = laygen.templates.get_template(icdrvl.cellname, libname=workinglib)
    for pname, p in t.pins.items():
        if p['netname']=='VDD':
            rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                    laygen.get_inst_pin_coord(icdrvl.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                    [x1, y0], rg_m3m4_thick)
            rv1, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                    laygen.get_inst_pin_coord(icdrvl.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                    [x1, y0+2], rg_m3m4_thick)
            rv2, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                    laygen.get_inst_pin_coord(icdrvr.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                    [x1, y0], rg_m3m4_thick)
            rv3, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                    laygen.get_inst_pin_coord(icdrvr.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                    [x1, y0+2], rg_m3m4_thick)
        if p['netname']=='VSS':
            rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                    laygen.get_inst_pin_coord(icdrvl.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                    [x1, y0+1], rg_m3m4_thick)
            rv1, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                    laygen.get_inst_pin_coord(icdrvl.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                    [x1, y0+3], rg_m3m4_thick)
            rv2, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                    laygen.get_inst_pin_coord(icdrvr.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                    [x1, y0+1], rg_m3m4_thick)
            rv3, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                    laygen.get_inst_pin_coord(icdrvr.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                    [x1, y0+3], rg_m3m4_thick)
    # vdd/vss - salatch
    num_vert_pwr = 20
    for i in range(num_vert_pwr):
        pname = 'VVDD' + str(2 * i)
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                laygen.get_inst_pin_coord(isa.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                [x1, y0], rg_m3m4_thick)
        rv1, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                laygen.get_inst_pin_coord(isa.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                [x1, y0+2], rg_m3m4_thick)
        pname = 'VVDD' + str(2 * i + 1)
        rv2, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                laygen.get_inst_pin_coord(isa.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                [x1, y0], rg_m3m4_thick)
        rv3, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                laygen.get_inst_pin_coord(isa.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                [x1, y0+2], rg_m3m4_thick)
        pname = 'VVSS' + str(2 * i)
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                laygen.get_inst_pin_coord(isa.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                [x1, y0+1], rg_m3m4_thick)
        rv1, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                laygen.get_inst_pin_coord(isa.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                [x1, y0+3], rg_m3m4_thick)
        pname = 'VVSS' + str(2 * i + 1)
        rv2, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                laygen.get_inst_pin_coord(isa.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                [x1, y0+1], rg_m3m4_thick)
        rv3, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                laygen.get_inst_pin_coord(isa.name, pname, rg_m3m4_thick, index=np.array([0, 0]), sort=True)[0],
                [x1, y0+3], rg_m3m4_thick)

    #pins
    laygen.pin(name='VREF<0>', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(rvref0.name, rg_m4m5), gridname=rg_m4m5)
    laygen.pin(name='VREF<1>', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(rvref1.name, rg_m4m5), gridname=rg_m4m5)
    laygen.pin(name='VREF<2>', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(rvref2.name, rg_m4m5), gridname=rg_m4m5)

    laygen.create_boundary_pin_form_rect(rclkb, rg_m4m5, "CLKB", laygen.layers['pin'][5], size=4, direction='bottom')
    laygen.create_boundary_pin_form_rect(routp, rg_m4m5, "OUTP", laygen.layers['pin'][5], size=4, direction='bottom')
    laygen.create_boundary_pin_form_rect(routm, rg_m4m5, "OUTM", laygen.layers['pin'][5], size=4, direction='bottom')
    laygen.create_boundary_pin_form_rect(rosp, rg_m2m3, "OSP", laygen.layers['pin'][3], size=4, direction='bottom')
    laygen.create_boundary_pin_form_rect(rosm, rg_m2m3, "OSM", laygen.layers['pin'][3], size=4, direction='bottom')
    for i in range(num_bits - 1):
        laygen.create_boundary_pin_form_rect(renl0[i], rg_m5m6, "ENL"+str(i)+"<0>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.create_boundary_pin_form_rect(renl1[i], rg_m5m6, "ENL"+str(i)+"<1>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.create_boundary_pin_form_rect(renl2[i], rg_m5m6, "ENL"+str(i)+"<2>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.create_boundary_pin_form_rect(renr0[i], rg_m5m6, "ENR"+str(i)+"<0>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.create_boundary_pin_form_rect(renr1[i], rg_m5m6, "ENR"+str(i)+"<1>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.create_boundary_pin_form_rect(renr2[i], rg_m5m6, "ENR"+str(i)+"<2>", laygen.layers['pin'][5], size=4, direction='bottom')

    laygen.create_boundary_pin_form_rect(rinp, rg_m5m6, "INP", laygen.layers['pin'][6], size=4, direction='right')
    laygen.create_boundary_pin_form_rect(rinm, rg_m5m6, "INM", laygen.layers['pin'][6], size=4, direction='left')

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
    rg_m2m3_thick = 'route_M2_M3_thick'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m3m4_thick = 'route_M3_M4_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m6m7 = 'route_M6_M7_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'


    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    mycell_list = []
    #capdrv generation
    cellname='sarafe'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarafe(laygen, objectname_pfix='CA0', workinglib=workinglib,
                    placement_grid=pg, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4_thick=rg_m3m4_thick,
                    routing_grid_m5m6=rg_m5m6, routing_grid_m6m7=rg_m6m7, num_bits=8, m_sa=8,
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
