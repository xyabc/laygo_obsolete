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

def generate_sarclkgen(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                       devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body,
                       m=2, m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate one-hot coded sar fsm """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    inv_name = 'inv_' + str(m) + 'x'
    iobuf_name = 'inv_' + str(4*m) + 'x'
    nand_name = 'nand_' + str(m) + 'x'
    sr_name = 'ndsr_2x'
    mux_name = 'mux2to1_' + str(m) + 'x'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    iinv0 = laygen.relplace(name="I" + objectname_pfix + 'INV0', templatename=inv_name,
                            gridname=pg, refinstname=itapl.name, template_libname=templib_logic)
    iinv1 = laygen.relplace(name="I" + objectname_pfix + 'INV1', templatename=inv_name,
                            gridname=pg, refinstname=iinv0.name, template_libname=templib_logic)
    isr0 = laygen.relplace(name="I" + objectname_pfix + 'SR0', templatename=sr_name,
                            gridname=pg, refinstname=iinv1.name, template_libname=templib_logic)
    inand0 = laygen.relplace(name="I" + objectname_pfix + 'ND0', templatename=nand_name,
                             gridname=pg, refinstname=isr0.name, template_libname=templib_logic)
    iinv2 = laygen.relplace(name="I" + objectname_pfix + 'INV2', templatename=inv_name,
                            gridname=pg, refinstname=inand0.name, template_libname=templib_logic)
    iinv3 = laygen.relplace(name="I" + objectname_pfix + 'INV3', templatename=inv_name,
                            gridname=pg, refinstname=iinv2.name, template_libname=templib_logic)
    iinv4 = laygen.relplace(name="I" + objectname_pfix + 'INV4', templatename=inv_name,
                            gridname=pg, refinstname=iinv3.name, template_libname=templib_logic)
    iinv5 = laygen.relplace(name="I" + objectname_pfix + 'INV5', templatename=inv_name,
                            gridname=pg, refinstname=iinv4.name, template_libname=templib_logic)

    gate_origin = laygen.get_inst_xy(iinv5.name, gridname=pg) \
                  + laygen.get_template_size(iinv5.cellname, gridname=pg, libname=templib_logic) * np.array([1, 0])
    inb0 = laygen.place("I" + objectname_pfix + 'NB0', devname_nmos_boundary, gridname = pg, xy=gate_origin)
    in0 = laygen.relplace("I" + objectname_pfix + 'N0', devname_nmos_body, pg, inb0.name, shape = np.array([int(m/2), 1]))
    inb1 = laygen.relplace("I" + objectname_pfix + 'NB1', devname_nmos_boundary, pg, in0.name)
    inb2 = laygen.relplace("I" + objectname_pfix + 'NB2', devname_nmos_boundary, pg, inb1.name)
    in1 = laygen.relplace("I" + objectname_pfix + 'N1', devname_nmos_body, pg, inb2.name, shape = np.array([int(m/2), 1]))
    inb3 = laygen.relplace("I" + objectname_pfix + 'NB3', devname_nmos_boundary, pg, in1.name)

    ipb0 = laygen.relplace("I"+objectname_pfix+'PB0', devname_pmos_boundary, pg, inb0.name, direction='top', transform='MX')
    ip0 = laygen.relplace("I"+objectname_pfix+'P0', devname_pmos_body, pg, ipb0.name, transform='MX', shape = np.array([int(m/2), 1]))
    ipb1 = laygen.relplace("I"+objectname_pfix+'PB1', devname_pmos_boundary, pg, ip0.name, transform='MX')
    ipb2 = laygen.relplace("I"+objectname_pfix+'PB2', devname_pmos_boundary, pg, ipb1.name, transform='MX')
    ip1 = laygen.relplace("I"+objectname_pfix + 'P1', devname_pmos_body, pg, ipb2.name, transform='MX', shape = np.array([int(m/2), 1]))
    ipb3 = laygen.relplace("I"+objectname_pfix+'PB3', devname_pmos_boundary, pg, ip1.name, transform='MX')

    origin2 = laygen.get_inst_xy(inb3.name, gridname=pg) \
              + laygen.get_template_size(inb3.cellname, gridname=pg) * np.array([1, 0])
    inand1 = laygen.place(name="I" + objectname_pfix + 'ND1', templatename=nand_name,
                          gridname=pg, xy=origin2, template_libname=templib_logic)
    iinv6 = laygen.relplace(name="I" + objectname_pfix + 'INV6', templatename=inv_name,
                            gridname=pg, refinstname=inand1.name, template_libname=templib_logic)

    iinv7 = laygen.relplace(name="I" + objectname_pfix + 'INV7', templatename=inv_name,
                            gridname=pg, refinstname=iinv6.name, template_libname=templib_logic)
    imux0 = laygen.relplace(name="I" + objectname_pfix + 'MUX0', templatename=mux_name,
                            gridname=pg, refinstname=iinv7.name, template_libname=templib_logic)
    iinv8 = laygen.relplace(name="I" + objectname_pfix + 'INV8', templatename=inv_name,
                            gridname=pg, refinstname=imux0.name, template_libname=templib_logic)
    iobuf0 = laygen.relplace(name="I" + objectname_pfix + 'IOBUF0', templatename=iobuf_name,
                              gridname=pg, refinstname=iinv8.name, template_libname=templib_logic)
    iobuf1 = laygen.relplace(name="I" + objectname_pfix + 'IOBUF1', templatename=iobuf_name,
                              gridname=pg, refinstname=iobuf0.name, template_libname=templib_logic)
    isp4x = []
    isp2x = []
    isp1x = []
    refi=iobuf1.name
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
    x0 = laygen.get_inst_xy(name=iinv0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=iobuf1.name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=iobuf1.cellname, gridname=rg_m3m4, libname=templib_logic)[0] - 1
    y0 = pdict[iinv0.name]['I'][0][1] + 0
    #inretnal routes - inv to nand
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['O'][0],
                                       pdict[inand0.name]['A'][0], y0 - 1, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv1.name]['O'][0],
                                       pdict[inand0.name]['B'][0], y0 + 0, rg_m3m4)
    # internal routes - sr
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['O'][0],
                                       pdict[isr0.name]['S'][0], y0 - 1, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv1.name]['O'][0],
                                       pdict[isr0.name]['R'][0], y0 + 0, rg_m3m4)
    # internal routes - and1
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand0.name]['O'][0],
                                       pdict[iinv2.name]['I'][0], y0 + 0, rg_m3m4) #DONE
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv2.name]['O'][0],
                                       pdict[iinv3.name]['I'][0], y0 + 1, rg_m3m4)
    # internal routes - and2
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[in0.name]['D0'][0]+np.array([2, 0]),
                                       pdict[inand1.name]['A'][0], y0 - 2, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv4.name]['O'][0],
                                       pdict[inand1.name]['B'][0], y0 + 3, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand1.name]['O'][0],
                                       pdict[iinv6.name]['I'][0], y0 - 3, rg_m3m4)  # PHIB0
    # internal routes - mux
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv6.name]['I'][0],
                                       pdict[imux0.name]['I0'][0], y0 + 2, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv7.name]['O'][0],
                                       pdict[imux0.name]['EN0'][0], y0 + 1, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv7.name]['I'][0],
                                       pdict[imux0.name]['EN1'][0], y0 + 4, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['O'][0],
                                       pdict[iinv8.name]['I'][0], y0 + 2, rg_m3m4)

    # internal routes - phi0 logic
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in0.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0', addvia0=True,
                 refinstindex1=np.array([int(m/2)-1, 0]), addvia1=True)
    for i in range(int(m / 2)):
        laygen.via(None, np.array([0, 0]), refinstname=in0.name, refpinname='G0', gridname=rg_m1m2, refinstindex=np.array([i, 0]))
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m1m2, refinstindex=np.array([i, 0]))
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, -2]), gridname0=rg_m2m3,
                 refinstname0=in0.name, refpinname0='G0', refinstname1=in0.name, refpinname1='G0', addvia0=True)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=ip0.name, refpinname0='G0', refinstname1=ip0.name, refpinname1='G0',
                 refinstindex1=np.array([int(m / 2) - 1, 0]), endstyle0='extend', endstyle1='extend')
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, -2]), gridname0=rg_m2m3,
                 refinstname0=ip0.name, refpinname0='G0', refinstname1=ip0.name, refpinname1='G0', addvia0=True)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, -2]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0', addvia0=True)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0',
                 refinstindex1=np.array([int(m / 2) - 1, 0]), endstyle0='extend', endstyle1='extend')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in0.name, refpinname0='D0',
                 refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([int(m/2)-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip0.name, refpinname0='D0',
                 refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([int(m/2)-1, 0]))
    for i in range(int(m / 2)):
        laygen.via(None, np.array([0, 0]), refinstname=in0.name, refpinname='D0', gridname=rg_m1m2, refinstindex=np.array([i, 0]))
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', gridname=rg_m1m2, refinstindex=np.array([i, 0]))
        laygen.via(None, np.array([0, 0]), refinstname=ip0.name, refpinname='D0', gridname=rg_m1m2, refinstindex=np.array([i, 0]))
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', gridname=rg_m1m2, refinstindex=np.array([i, 0]))
    rphi0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2, 0]), xy1=np.array([2, 0]), gridname0=rg_m2m3,
                         refinstname0=in0.name, refpinname0='D0', refinstname1=ip0.name, refpinname1='D0', addvia0=True,
                         addvia1=True)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[ip0.name]['G0'][0],
                                       pdict[iinv4.name]['O'][0], y0 + 3, rg_m3m4)  # rstb
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[ip1.name]['G0'][0],
                                       pdict[iinv5.name]['O'][0], y0 + 2, rg_m3m4)  # upb
    for i in range(int(m / 2)):
        laygen.via(None, np.array([0, 0]), refinstname=ip0.name, refpinname='G0', gridname=rg_m1m2, refinstindex=np.array([i, 0]))
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G0', gridname=rg_m1m2, refinstindex=np.array([i, 0]))
        # power and ground routes
        xy_s0 = laygen.get_template_pin_coord(in0.cellname, 'S0', rg_m1m2)[0, :]
        xy_s1 = laygen.get_template_pin_coord(in0.cellname, 'S1', rg_m1m2)[0, :]
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=in0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=in0.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s1 * np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=in0.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                     refinstname1=in0.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=ip0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip0.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s1 * np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=ip0.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                     refinstname1=ip0.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in0.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in0.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip0.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip0.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        xy_s0 = laygen.get_template_pin_coord(in1.cellname, 'S0', rg_m1m2)[0, :]
        xy_s1 = laygen.get_template_pin_coord(in1.cellname, 'S1', rg_m1m2)[0, :]
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s1 * np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=ip1.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s1 * np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=ip1.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)


    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[in0.name]['G0'][0],
                                       pdict[inand0.name]['O'][0], y0 + 0, rg_m3m4) #DONE

    # input routes
    rv0, rsaopb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['I'][0],
                                   np.array([x0, y0 + 2]), rg_m3m4)
    rv0, rsaomb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv1.name]['I'][0],
                                   np.array([x0, y0 + 1]), rg_m3m4)
    rv0, rrst0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv4.name]['I'][0],
                                   np.array([x0, y0 - 2]), rg_m3m4)
    rv0, rup0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv5.name]['I'][0],
                                   np.array([x0, y0 - 3]), rg_m3m4)
    rv0, rextsel_clk0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv7.name]['I'][0],
                                        np.array([x0, y0 + 4]), rg_m3m4)
    rv0, rextclk0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['I1'][0],
                                    np.array([x0, y0 + 5]), rg_m3m4)

    #output routes
    rv0, rcompout0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isr0.name]['Q'][0],
                                  np.array([x1, y0 + 6]), rg_m3m4)
    rv0, rdone0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand0.name]['O'][0],
                                  np.array([x1, y0 + 0]), rg_m3m4)
    rv0, rdoneb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv3.name]['I'][0],
                                  np.array([x1, y0 - 4]), rg_m3m4)
    rv0, rdone_prb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv3.name]['O'][0],
                                  np.array([x1, y0 - 1]), rg_m3m4)
    rv0, rclk_prb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv6.name]['O'][0],
                                  np.array([x1, y0 - 2]), rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv8.name]['O'][0],
                                       pdict[iobuf0.name]['I'][0], y0 + 1, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iobuf0.name]['O'][0],
                                       pdict[iobuf1.name]['I'][0], y0 + 2, rg_m3m4)
    v0, rclkob0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iobuf0.name]['O'][0],
                                  np.array([x1, y0 + 2]), rg_m3m4)
    v0, rclko0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iobuf1.name]['O'][0],
                                  np.array([x1, y0 + 1]), rg_m3m4)

    # pins
    laygen.create_boundary_pin_form_rect(rsaopb0, rg_m3m4, "SAOPB", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rsaomb0, rg_m3m4, "SAOMB", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rrst0, rg_m3m4, "RST", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rup0, rg_m3m4, "UP", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rextsel_clk0, rg_m3m4, "EXTSEL_CLK", laygen.layers['pin'][4], size=6, direction='left')
    laygen.create_boundary_pin_form_rect(rextclk0, rg_m3m4, "EXTCLK", laygen.layers['pin'][4], size=6, direction='left')

    laygen.create_boundary_pin_form_rect(rcompout0, rg_m3m4, "COMPOUT", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rdone0, rg_m3m4, "DONE", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rdoneb0, rg_m3m4, "DONEB", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rdone_prb0, rg_m3m4, "DONEPRB", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rclk_prb0, rg_m3m4, "CLKPRB", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rclkob0, rg_m3m4, "CLKOB", laygen.layers['pin'][4], size=6, direction='right')
    laygen.create_boundary_pin_form_rect(rclko0, rg_m3m4, "CLKO", laygen.layers['pin'][4], size=6, direction='right')

    # power route (horizontal)
    #create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=itapl, inst_right=itapr)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=itapl.name, refpinname0='VDD', refinstname1=itapr.name, refpinname1='VDD')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=itapl.name, refpinname0='VSS', refinstname1=itapr.name, refpinname1='VSS')

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
    #generation (2 step)
    cellname='sarclkgen'
    print(cellname+" generating")
    mycell_list.append(cellname)
    #1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkgen(laygen, objectname_pfix='FSM0', templib_logic=logictemplib, placement_grid=pg,
                       routing_grid_m3m4=rg_m3m4,
                       devname_nmos_boundary='nmos4_fast_boundary',
                       devname_nmos_body='nmos4_fast_center_nf2',
                       devname_pmos_boundary='pmos4_fast_boundary',
                       devname_pmos_body='pmos4_fast_center_nf2',
                       m=2, m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]  \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x=int(m_space/4)
    m_space_2x=int((m_space-m_space_4x*4)/2)
    m_space_1x=int(m_space-m_space_4x*4-m_space_2x*2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkgen(laygen, objectname_pfix='FSM0', templib_logic=logictemplib, placement_grid=pg,
                       routing_grid_m3m4=rg_m3m4,
                       devname_nmos_boundary='nmos4_fast_boundary',
                       devname_nmos_body='nmos4_fast_center_nf2',
                       devname_pmos_boundary='pmos4_fast_boundary',
                       devname_pmos_body='pmos4_fast_center_nf2',
                       m=2, m_space_4x=m_space_4x, m_space_2x=m_space_2x, m_space_1x=m_space_1x, origin=np.array([0, 0]))
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
