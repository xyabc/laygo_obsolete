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

def generate_boundary(laygen, objectname_pfix, placement_grid,
                      devname_bottom, devname_top, devname_left, devname_right,
                      shape_bottom=None, shape_top=None, shape_left=None, shape_right=None,
                      transform_bottom=None, transform_top=None, transform_left=None, transform_right=None,
                      origin=np.array([0, 0])):
    #generate a boundary structure to resolve boundary design rules
    pg = placement_grid
    #parameters
    if shape_bottom == None:
        shape_bottom = [np.array([1, 1]) for d in devname_bottom]
    if shape_top == None:
        shape_top = [np.array([1, 1]) for d in devname_top]
    if shape_left == None:
        shape_left = [np.array([1, 1]) for d in devname_left]
    if shape_right == None:
        shape_right = [np.array([1, 1]) for d in devname_right]
    if transform_bottom == None:
        transform_bottom = ['R0' for d in devname_bottom]
    if transform_top == None:
        transform_top = ['R0' for d in devname_top]
    if transform_left == None:
        transform_left = ['R0' for d in devname_left]
    if transform_right == None:
        transform_right = ['R0' for d in devname_right]

    #bottom
    dev_bottom=[]
    dev_bottom.append(laygen.place("I" + objectname_pfix + 'BNDBTM0', devname_bottom[0], pg, xy=origin,
                      shape=shape_bottom[0], transform=transform_bottom[0]))
    for i, d in enumerate(devname_bottom[1:]):
        dev_bottom.append(laygen.relplace("I" + objectname_pfix + 'BNDBTM'+str(i+1), d, pg, dev_bottom[-1].name,
                                          shape=shape_bottom[i+1], transform=transform_bottom[i+1]))
    dev_left=[]
    dev_left.append(laygen.relplace("I" + objectname_pfix + 'BNDLFT0', devname_left[0], pg, dev_bottom[0].name, direction='top',
                                    shape=shape_left[0], transform=transform_left[0]))
    for i, d in enumerate(devname_left[1:]):
        dev_left.append(laygen.relplace("I" + objectname_pfix + 'BNDLFT'+str(i+1), d, pg, dev_left[-1].name, direction='top',
                                        shape=shape_left[i+1], transform=transform_left[i+1]))
    dev_right=[]
    dev_right.append(laygen.relplace("I" + objectname_pfix + 'BNDRHT0', devname_right[0], pg, dev_bottom[-1].name, direction='top',
                                     shape=shape_right[0], transform=transform_right[0]))
    for i, d in enumerate(devname_right[1:]):
        dev_right.append(laygen.relplace("I" + objectname_pfix + 'BNDRHT'+str(i+1), d, pg, dev_right[-1].name, direction='top',
                                         shape=shape_right[i+1], transform=transform_right[i+1]))
    dev_top=[]
    dev_top.append(laygen.relplace("I" + objectname_pfix + 'BNDTOP0', devname_top[0], pg, dev_left[-1].name, direction='top',
                                   shape=shape_top[0], transform=transform_top[0]))
    for i, d in enumerate(devname_top[1:]):
        dev_top.append(laygen.relplace("I" + objectname_pfix + 'BNDTOP'+str(i+1), d, pg, dev_top[-1].name,
                                       shape=shape_top[i+1], transform=transform_top[i+1]))
    return [dev_bottom, dev_top, dev_left, dev_right]

def generate_sarabe_dualdelay(laygen, objectname_pfix, workinglib, placement_grid, routing_grid_m2m3, 
                              routing_grid_m3m4_thick, routing_grid_m4m5_thick, routing_grid_m5m6_thick,
                              routing_grid_m4m5, num_bits=9, origin=np.array([0, 0])):
    """generate sar backend """
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m3m4_thick = routing_grid_m3m4_thick
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m4m5 = routing_grid_m4m5

    sarfsm_name = 'sarfsm_'+str(num_bits)+'b'
    sarlogic_name = 'sarlogic_wret_array_'+str(num_bits)+'b'
    sarclkdelay_name = 'sarclkdelay_compact_dual'
    sarclkgen_name = 'sarclkgen_static'
    sarret_name = 'sarret_'+str(num_bits)+'b'
    space_name = 'space'

    xy0=laygen.get_template_size(name=space_name, gridname=pg, libname=workinglib)
    xsp=xy0[0]
    ysp=xy0[1]

    # placement
    core_origin = origin + laygen.get_template_size('boundary_bottomleft', pg)
    isp=[]
    devname_bnd_left = []
    devname_bnd_right = []
    transform_bnd_left = []
    transform_bnd_right = []
    #ret
    iret=laygen.place(name="I" + objectname_pfix + 'RET0', templatename=sarret_name,
                         gridname=pg, xy=core_origin, template_libname=workinglib)
    refi = iret.name
    yret = int(laygen.get_template_size(name=sarret_name, gridname=pg, libname=workinglib)[1] / ysp)
    for i in range(yret): #boundary cells
        if i % 2 == 0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    # space insertion if number of rows is odd
    if not yret % 2 == 0:
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
        devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']
    #fsm
    ifsm=laygen.relplace(name="I" + objectname_pfix + 'FSM0', templatename=sarfsm_name,
                         gridname=pg, refinstname=refi, direction='top', template_libname=workinglib)
    refi = ifsm.name
    yfsm = int(laygen.get_template_size(name=sarfsm_name, gridname=pg, libname=workinglib)[1] / ysp)
    for i in range(yfsm): #boundary cells
        if i % 2 == 0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    # space insertion if number of rows is odd
    if not yfsm % 2 == 0:
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
        devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']
    #additional space for routing area
    isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                               gridname=pg, refinstname=refi, direction='top', transform='R0',
                               template_libname=workinglib))
    refi = isp[-1].name
    isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                               gridname=pg, refinstname=refi, direction='top', transform='MX',
                               template_libname=workinglib))
    refi = isp[-1].name
    devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left', 'pmos4_fast_left', 'nmos4_fast_left']
    devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right', 'pmos4_fast_right', 'nmos4_fast_right']
    transform_bnd_left += ['R0', 'MX', 'R0', 'MX']
    transform_bnd_right += ['R0', 'MX', 'R0', 'MX']
    # sarlogic
    isl = laygen.relplace(name="I" + objectname_pfix + 'SL0', templatename=sarlogic_name,
                          gridname=pg, refinstname=refi, direction='top', template_libname=workinglib)
    refi = isl.name
    ysl = int(laygen.get_template_size(name=sarlogic_name, gridname=pg, libname=workinglib)[1] / ysp)
    for i in range(ysl): #boundary cells
        if i % 2 == 0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    # space insertion if number of rows is odd
    if not ysl % 2 == 0:
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
        devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']
    #clkdelay & clkgen
    ickd = laygen.relplace(name="I" + objectname_pfix + 'CKD0', templatename=sarclkdelay_name,
                          gridname=pg, refinstname=refi, direction='top', template_libname=workinglib)
    refi = ickd.name
    ickg = laygen.relplace(name="I" + objectname_pfix + 'CKG0', templatename=sarclkgen_name,
                           gridname=pg, refinstname=refi, direction='top', transform='MX', template_libname=workinglib)
    refi = ickg.name
    # space insertion if number of rows is odd
    yck=(laygen.get_template_size(name=sarclkdelay_name, gridname=pg, libname=workinglib)[1]+\
         laygen.get_template_size(name=sarclkgen_name, gridname=pg, libname=workinglib)[1])/ysp
    for i in range(int(yck)): #boundary cells
        if i % 2 == 0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    if not int(yck / ysp) % 2 == 0:
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
        devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']
    #additional space for routing area
    isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                               gridname=pg, refinstname=refi, direction='top', transform='R0',
                               template_libname=workinglib))
    refi = isp[-1].name
    isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                               gridname=pg, refinstname=refi, direction='top', transform='MX',
                               template_libname=workinglib))
    refi = isp[-1].name
    devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left', 'pmos4_fast_left', 'nmos4_fast_left']
    devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right', 'pmos4_fast_right', 'nmos4_fast_right']
    transform_bnd_left += ['R0', 'MX', 'R0', 'MX']
    transform_bnd_right += ['R0', 'MX', 'R0', 'MX']
    
    # boundaries
    m_bnd = int(xsp / laygen.get_template_size('boundary_bottom', gridname=pg)[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=devname_bnd_left,
                            transform_left=transform_bnd_left,
                            devname_right=devname_bnd_right,
                            transform_right=transform_bnd_right,
                            origin=origin)
    #route
    #reference coordinates
    pdict_m3m4 = laygen.get_inst_pin_coord(None, None, rg_m3m4)
    pdict_m4m5 = laygen.get_inst_pin_coord(None, None, rg_m4m5)
    pdict_m5m6 = laygen.get_inst_pin_coord(None, None, rg_m5m6)
    x_right = laygen.get_inst_xy(name=ifsm.name, gridname=rg_m5m6)[0]\
             +laygen.get_template_size(name=ifsm.cellname, gridname=rg_m5m6, libname=workinglib)[0] - 1
    y_top = laygen.get_inst_xy(name=ickg.name, gridname=rg_m5m6)[1]-1
    xysl = laygen.get_inst_xy(name=isl.name, gridname=rg_m5m6)
    xyfsm = laygen.get_inst_xy(name=ifsm.name, gridname=rg_m5m6)
    xyret = laygen.get_inst_xy(name=iret.name, gridname=rg_m5m6)
    # ckdly route
    # rst
    rh0, rh0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                               pdict_m4m5[ickd.name]['RST'][0], pdict_m4m5[isl.name]['RST'][0], rg_m4m5)
    # sb
    rh0, rh0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                               pdict_m4m5[ickd.name]['SB'][0], pdict_m4m5[isl.name]['SB<4>'][0], rg_m4m5)
    # done
    [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m5m6[ickg.name]['DONE'][0],
                                           pdict_m5m6[ickd.name]['I'][0],
                                           pdict_m5m6[ickd.name]['I'][0][0]+2, rg_m4m5)
    # up
    [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m5m6[ickg.name]['UP'][0],
                                           pdict_m5m6[ickd.name]['O'][0],
                                           pdict_m5m6[ickg.name]['UP'][0][0], rg_m4m5)
    # ckgen to sl route
    # saopb/saomb
    [rh0, rsaopb0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m5m6[ickg.name]['SAOPB'][0],
                                           pdict_m5m6[isl.name]['SAOPB'][0],
                                           pdict_m5m6[ickg.name]['SAOPB'][0][0]+1, rg_m4m5)
    [rh0, rsaomb0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m5m6[ickg.name]['SAOMB'][0],
                                           pdict_m5m6[isl.name]['SAOMB'][0],
                                           pdict_m5m6[ickg.name]['SAOMB'][0][0]+2, rg_m4m5)
    # ckgen to fsm route
    # sarclk
    rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                               pdict_m5m6[ickg.name]['CLKO'][0], pdict_m5m6[ifsm.name]['CLK'][0], rg_m4m5)
    # fsm to sl route
    # sb
    for i in range(num_bits):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[ifsm.name]['SB<'+str(i)+'>'][0],
                                           pdict_m5m6[isl.name]['SB<'+str(i)+'>'][0], xysl[1]-i-1, rg_m5m6)
    # rst 
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[ifsm.name]['RST'][0],
                                       pdict_m5m6[isl.name]['RST'][0], 
                                       xyfsm[1] - num_bits - 2, rg_m5m6)
                                       #pdict_m5m6[ifsm.name]['RST'][1][1], rg_m5m6)
    # ckg to sl route
    rh0, rrst0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                               pdict_m4m5[ickg.name]['RST'][0], pdict_m4m5[isl.name]['RST'][0], rg_m4m5)
    #output
    # zp/zm/zmid
    for i in range(num_bits):
        rzp0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m4m5[isl.name]['ZP<'+str(i)+'>'][0],
                            xy1=np.array([pdict_m4m5[isl.name]['ZP<'+str(i)+'>'][0][0], y_top]), gridname0=rg_m5m6)
        laygen.create_boundary_pin_form_rect(rzp0, rg_m5m6, 'ZP<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='top')
        rzm0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m4m5[isl.name]['ZM<'+str(i)+'>'][0],
                            xy1=np.array([pdict_m4m5[isl.name]['ZM<'+str(i)+'>'][0][0], y_top]), gridname0=rg_m5m6)
        laygen.create_boundary_pin_form_rect(rzm0, rg_m5m6, 'ZM<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='top')
        rzmid0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m4m5[isl.name]['ZMID<'+str(i)+'>'][0],
                            xy1=np.array([pdict_m4m5[isl.name]['ZMID<'+str(i)+'>'][0][0], y_top]), gridname0=rg_m5m6)
        laygen.create_boundary_pin_form_rect(rzmid0, rg_m5m6, 'ZMID<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='top')
    # ckdsel
    for i in range(2):
        rh0, rclkdsel0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                         pdict_m4m5[ickd.name]['SEL0<' + str(i) + '>'][0],
                                         np.array([pdict_m4m5[isl.name]['RETO<7>'][1][0]+4+2*i, 0]), rg_m4m5)
        laygen.create_boundary_pin_form_rect(rclkdsel0, rg_m4m5, 'CKDSEL0<' + str(i) + '>', laygen.layers['pin'][5], size=6,direction='bottom')
        rh0, rclkdsel0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                         pdict_m4m5[ickd.name]['SEL1<' + str(i) + '>'][0],
                                         np.array([pdict_m4m5[isl.name]['RETO<7>'][1][0]+4+2*i+4, 0]), rg_m4m5)
        laygen.create_boundary_pin_form_rect(rclkdsel0, rg_m4m5, 'CKDSEL1<' + str(i) + '>', laygen.layers['pin'][5], size=6,direction='bottom')
    # SAOPB/SAOMB
    laygen.create_boundary_pin_form_rect(rsaopb0, rg_m4m5, 'SAOPB', laygen.layers['pin'][5], size=6, direction='top')
    laygen.create_boundary_pin_form_rect(rsaomb0, rg_m4m5, 'SAOMB', laygen.layers['pin'][5], size=6, direction='top')
    # extclk, extsel_clk
    rh0, rextclk0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                    pdict_m4m5[ickg.name]['EXTCLK'][0],
                                    np.array([pdict_m4m5[ickg.name]['EXTCLK'][0][0]-2+16, 0]), rg_m4m5)
    laygen.create_boundary_pin_form_rect(rextclk0, rg_m4m5, 'EXTCLK', laygen.layers['pin'][5], size=6, direction='bottom')
    rh0, rextsel_clk0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                    pdict_m4m5[ickg.name]['EXTSEL_CLK'][0],
                                    np.array([pdict_m4m5[ickg.name]['EXTSEL_CLK'][0][0]-4+16, 0]), rg_m4m5)
    laygen.create_boundary_pin_form_rect(rextsel_clk0, rg_m4m5, 'EXTSEL_CLK', laygen.layers['pin'][5], size=6, direction='bottom')
    # fsm to ret (rst)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[isl.name]['RST'][0],
                                       pdict_m5m6[iret.name]['CLK'][0], xyfsm[1] - num_bits - 2, rg_m5m6)
    rrstout0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m5m6[iret.name]['CLK'][0],
                            xy1=np.array([pdict_m5m6[iret.name]['CLK'][0][0], 0]), gridname0=rg_m5m6)
    # fsm to ret (data)
    for i in range(num_bits):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[isl.name]['RETO<'+str(i)+'>'][0],
                                           pdict_m5m6[iret.name]['IN<'+str(i)+'>'][0], xyfsm[1]-i-1, rg_m5m6)
    # adcout
    for i in range(num_bits):
        radco0 = laygen.route(None, laygen.layers['metal'][5],
                             xy0=pdict_m4m5[iret.name]['OUT<'+str(i)+'>'][0],
                             xy1=np.array([pdict_m4m5[iret.name]['OUT<'+str(i)+'>'][0][0], 0]), gridname0=rg_m5m6)
        laygen.create_boundary_pin_form_rect(radco0, rg_m4m5, 'ADCOUT<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='bottom')
    # rst
    laygen.create_boundary_pin_form_rect(rrst0, rg_m5m6, 'RST', laygen.layers['pin'][5], size=6, direction='top')
    # clkprb
    rh0, rclkprb0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                    pdict_m4m5[ickg.name]['CLKPRB'][0],
                                    np.array([pdict_m4m5[isl.name]['RETO<7>'][1][0]+2, 0]), rg_m4m5)
    laygen.create_boundary_pin_form_rect(rclkprb0, rg_m4m5, 'CLKPRB', laygen.layers['pin'][5], size=6,direction='bottom')
    # probe outputs
    laygen.pin(name='COMPOUT', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['COMPOUT'], gridname=rg_m4m5)
    laygen.pin(name='UP', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['UP'], gridname=rg_m4m5)
    laygen.pin(name='DONE', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['DONE'], gridname=rg_m4m5)
    laygen.pin(name='SARCLK', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['CLKO'], gridname=rg_m4m5)
    rh0, rsclkb0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                   pdict_m4m5[ickg.name]['CLKOB'][0],
                                   np.array([pdict_m4m5[ickg.name]['CLKOB'][1][0]+12, y_top]), rg_m4m5)
    laygen.create_boundary_pin_form_rect(rsclkb0, rg_m4m5, 'SARCLKB', laygen.layers['pin'][5], size=6, direction='top')
    for i in range(num_bits):
        laygen.pin(name='SB<' + str(i) + '>', layer=laygen.layers['pin'][5],
                   xy=pdict_m5m6[isl.name]['SB<' + str(i) + '>'], gridname=rg_m5m6)
    # vdd/vss
    # m3
    rvdd_m3=[]
    rvss_m3=[]
    i=0
    for p in pdict_m3m4[iret.name]:
        if p.startswith('VDD'):
            laygen.pin(name='VDD_M3' + str(i), layer=laygen.layers['pin'][3],
                       xy=np.vstack((pdict_m3m4[iret.name][p][0], pdict_m3m4[ickg.name][p][0])), gridname=rg_m3m4, netname='VDD')
            i+=1
            r0=laygen.route(None, laygen.layers['metal'][3], xy0=pdict_m3m4[iret.name][p][0], xy1=pdict_m3m4[isp[-1].name][p][0],
                            gridname0=rg_m3m4)
            rvdd_m3.append(r0)
    i=0
    for p in pdict_m3m4[iret.name]:
        if p.startswith('VSS'):
            laygen.pin(name='VSS_M3' + str(i), layer=laygen.layers['pin'][3],
                       xy=np.vstack((pdict_m3m4[iret.name][p][0], pdict_m3m4[ickg.name][p][0])), gridname=rg_m3m4, netname='VSS')
            i+=1
            r0=laygen.route(None, laygen.layers['metal'][3], xy0=pdict_m3m4[iret.name][p][0], xy1=pdict_m3m4[isp[-1].name][p][0],
                            gridname0=rg_m3m4)
            rvss_m3.append(r0)
    # m4
    inst_exclude=[iret,ifsm,isl,ickd,ickg]
    x0 = laygen.get_inst_xy(name=bnd_left[0].name, gridname=rg_m3m4_thick)[0]
    x0b = laygen.get_inst_xy(name=bnd_left[0].name, gridname=rg_m3m4_thick)[0]\
         +laygen.get_template_size(name=bnd_left[0].cellname, gridname=rg_m3m4_thick, libname=utemplib)[0]\
         +laygen.get_template_size(name='tap', gridname=rg_m3m4_thick, libname=logictemplib)[0]-1
    y0 = laygen.get_inst_xy(name=bnd_left[0].name, gridname=rg_m3m4_thick)[1]
    x1 = laygen.get_inst_xy(name=bnd_right[0].name, gridname=rg_m3m4_thick)[0]\
         +laygen.get_template_size(name=bnd_right[0].cellname, gridname=rg_m3m4_thick, libname=utemplib)[0]
    x1a = laygen.get_inst_xy(name=bnd_right[0].name, gridname=rg_m3m4_thick)[0]\
         -laygen.get_template_size(name='tap', gridname=rg_m3m4_thick, libname=logictemplib)[0]+1
    y1 = laygen.get_inst_xy(name=bnd_left[-1].name, gridname=rg_m3m4_thick)[1]
    for i in range(y1-y0):
        #check if y is not in the exclude area
        trig=1
        for iex in inst_exclude:
            if iex.transform=='MX':
                yex0 = laygen.get_inst_xy(name=iex.name, gridname=rg_m3m4_thick)[1]-1\
                       -laygen.get_template_size(name=iex.cellname, gridname=rg_m3m4_thick, libname=workinglib)[1]
                yex1 = laygen.get_inst_xy(name=iex.name, gridname=rg_m3m4_thick)[1]+1
            else:
                yex0 = laygen.get_inst_xy(name=iex.name, gridname=rg_m3m4_thick)[1]-1
                yex1 = laygen.get_inst_xy(name=iex.name, gridname=rg_m3m4_thick)[1]+1\
                       +laygen.get_template_size(name=iex.cellname, gridname=rg_m3m4_thick, libname=workinglib)[1]
            if y0+i > yex0 and y0+i < yex1: #exclude
                trig=0 
        if trig==1:
            r0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0, y0+i]), xy1=np.array([x1, y0+i]), 
                            gridname0=rg_m3m4_thick)
        else:
            r0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0, y0+i]), xy1=np.array([x0b, y0+i]), 
                            gridname0=rg_m3m4_thick)
            r0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x1a, y0+i]), xy1=np.array([x1, y0+i]), 
                            gridname0=rg_m3m4_thick)
        if i%2==0: 
            rvia=rvdd_m3 
        else: 
            rvia=rvss_m3
        for rv in rvia:
            xv0 = laygen.get_rect_xy(name=rv.name, gridname=rg_m3m4_thick)[0][0]
            laygen.via(None, np.array([xv0, y0+i]), gridname=rg_m3m4_thick)
    #m5 
    rvdd_m5_l=[]
    rvss_m5_l=[]
    rvdd_m5_r=[]
    rvss_m5_r=[]
    x0 = 1
    x0b = laygen.get_inst_xy(name=bnd_left[0].name, gridname=rg_m4m5_thick)[0]\
         +laygen.get_template_size(name=bnd_left[0].cellname, gridname=rg_m4m5_thick, libname=utemplib)[0]\
         +laygen.get_template_size(name='tap', gridname=rg_m4m5_thick, libname=logictemplib)[0]-1
    y0 = laygen.get_inst_xy(name=bnd_left[0].name, gridname=rg_m4m5_thick)[1]
    x1 = laygen.get_inst_xy(name=bnd_right[0].name, gridname=rg_m4m5_thick)[0] - 1\
         +laygen.get_template_size(name=bnd_right[0].cellname, gridname=rg_m4m5_thick, libname=utemplib)[0]\
         +laygen.get_template_size(name='tap', gridname=rg_m4m5_thick, libname=logictemplib)[0]-1-1
    x1a = laygen.get_inst_xy(name=bnd_right[0].name, gridname=rg_m4m5_thick)[0]\
         -laygen.get_template_size(name='tap', gridname=rg_m4m5_thick, libname=logictemplib)[0]+1+1
    y1 = laygen.get_inst_xy(name=bnd_left[-1].name, gridname=rg_m4m5_thick)[1]
    for i in range(x0, x0b):
        r0=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([i, y0]), xy1=np.array([i, y1]), 
                        gridname0=rg_m4m5_thick)
        nvia=int((y1-y0)/2)
        if i%2==0:
            nvia_start=0
            rvdd_m5_l.append(r0)
        else:
            nvia_start=1
            rvss_m5_l.append(r0)
        for j in range(nvia):
            laygen.via(None, np.array([i, nvia_start+2*j+y0]), gridname=rg_m4m5_thick)
    for i in range(x1a, x1):
        r0=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([i, y0]), xy1=np.array([i, y1]), 
                        gridname0=rg_m4m5_thick)
        nvia=int((y1-y0)/2)
        if i%2==0:
            nvia_start=0
            rvdd_m5_r.append(r0)
        else:
            nvia_start=1
            rvss_m5_r.append(r0)
        for j in range(nvia):
            laygen.via(None, np.array([i, nvia_start+2*j+y0]), gridname=rg_m4m5_thick)
    #m6 
    rvdd_m6=[]
    rvss_m6=[]
    inst_reference=[iret,ifsm,isl]
    #num_route=[10,10]
    num_route=[]
    for i, inst in enumerate(inst_reference):
        #num_route.append(laygen.get_inst_xy(name=inst.name, gridname=rg_m5m6_thick)[1]-2)
        num_route.append(laygen.get_template_size(name=inst.cellname, gridname=rg_m5m6_thick, libname=workinglib)[1]-2)
    x0 = laygen.get_inst_xy(name=bnd_left[0].name, gridname=rg_m5m6_thick)[0]
    x1 = laygen.get_inst_xy(name=bnd_right[0].name, gridname=rg_m5m6_thick)[0]\
         +laygen.get_template_size(name=bnd_right[0].cellname, gridname=rg_m5m6_thick, libname=utemplib)[0]
    n_vdd_m6=0 #number for m6 wires
    n_vss_m6=0 #number for m6 wires
    for i, inst in enumerate(inst_reference):
        for j in range(num_route[i]):
            y0 = laygen.get_inst_xy(name=inst.name, gridname=rg_m5m6_thick)[1]+1
            r0=laygen.route(None, laygen.layers['metal'][6], xy0=np.array([x0, y0+j]), xy1=np.array([x1, y0+j]), 
                            gridname0=rg_m5m6_thick)
            if j%2==0: 
                rvdd_m6.append(r0)
                xy0 = laygen.get_rect_xy(name=r0.name, gridname=rg_m5m6_thick)
                laygen.pin(name='VDD_M6' + str(n_vdd_m6), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VDD')
                n_vdd_m6+=1
                for rv in rvdd_m5_l:
                    xv0 = laygen.get_rect_xy(name=rv.name, gridname=rg_m5m6_thick)[0][0]
                    laygen.via(None, np.array([xv0, y0+j]), gridname=rg_m5m6_thick)
                for rv in rvdd_m5_r:
                    xv0 = laygen.get_rect_xy(name=rv.name, gridname=rg_m5m6_thick)[0][0]
                    laygen.via(None, np.array([xv0, y0+j]), gridname=rg_m5m6_thick)
            else: 
                rvss_m6.append(r0)
                xy0 = laygen.get_rect_xy(name=r0.name, gridname=rg_m5m6_thick)
                laygen.pin(name='VSS_M6' + str(n_vss_m6), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VSS')
                n_vss_m6+=1
                for rv in rvss_m5_l:
                    xv0 = laygen.get_rect_xy(name=rv.name, gridname=rg_m5m6_thick)[0][0]
                    laygen.via(None, np.array([xv0, y0+j]), gridname=rg_m5m6_thick)
                for rv in rvss_m5_r:
                    xv0 = laygen.get_rect_xy(name=rv.name, gridname=rg_m5m6_thick)[0][0]
                    laygen.via(None, np.array([xv0, y0+j]), gridname=rg_m5m6_thick)
    '''
    for i in range(y1-y0):
        #check if y is not in the exclude area
        r0=laygen.route(None, laygen.layers['metal'][6], xy0=np.array([x0, y0+i]), xy1=np.array([x1, y0+i]), 
                            gridname0=rg_m5m6_thick)
        if i%2==0: 
            rvia=rvdd_m6 
        else: 
            rvia=rvss_m6
        for rv in rvia:
            xv0 = laygen.get_rect_xy(name=rv.name, gridname=rg_m5m6_thick)[0][0]
            laygen.via(None, np.array([xv0, y0+i]), gridname=rg_m5m6_thick)
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
    #sarabe generation
    cellname='sarabe_dualdelay_'+str(num_bits)+'b'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarabe_dualdelay(laygen, objectname_pfix='CA0', workinglib=workinglib,
                    placement_grid=pg, routing_grid_m2m3=rg_m2m3, 
                    routing_grid_m3m4_thick=rg_m3m4_thick, routing_grid_m4m5_thick=rg_m4m5_thick, routing_grid_m5m6_thick=rg_m5m6_thick, 
                    routing_grid_m4m5=rg_m4m5, num_bits=num_bits, origin=np.array([0, 0]))
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
