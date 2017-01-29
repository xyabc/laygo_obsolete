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
    dev_right=[]
    return [dev_bottom, dev_top, dev_left, dev_right]

def generate_sarabe(laygen, objectname_pfix, workinglib, placement_grid, routing_grid_m2m3,
                    routing_grid_m4m5, num_bits=8, num_bits_row=4, origin=np.array([0, 0])):
    """generate sar backend """
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m4m5 = routing_grid_m4m5
    num_row=int(num_bits/num_bits_row)

    sarret_name = 'sarret'
    sarfsm_name = 'sarfsm'
    sarlogic_name = 'sarlogic_array_8b'
    sarclkdelay_name = 'sarclkdelay'
    sarclkgen_name = 'sarclkgen'
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
    refi=iret.name
    yret=int(laygen.get_template_size(name=sarret_name, gridname=pg, libname=workinglib)[1] / ysp)
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
    #space insertion if number of rows is odd
    if not yret % 2 == 0: #boundary cells
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi=isp[-1].name
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
    x_right = laygen.get_inst_xy(name=iret.name, gridname=rg_m5m6)[0]\
             +laygen.get_template_size(name=iret.cellname, gridname=rg_m5m6, libname=workinglib)[0] - 1
    y_top = laygen.get_inst_xy(name=ickg.name, gridname=rg_m5m6)[1]-1
    xysl = laygen.get_inst_xy(name=isl.name, gridname=rg_m5m6)
    xyret = laygen.get_inst_xy(name=iret.name, gridname=rg_m5m6)
    xyfsm = laygen.get_inst_xy(name=ifsm.name, gridname=rg_m5m6)
    # ret to fsm (clk)
    [rrst0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iret.name]['CLK'][0], pdict_m5m6[ifsm.name]['RST'][0], xyfsm[1], rg_m5m6)
    # ckgen to ckdly route
    # done
    [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m5m6[ickg.name]['DONE'][0],
                                           pdict_m5m6[ickd.name]['I'][0],
                                           pdict_m5m6[ickd.name]['I'][0][0], rg_m4m5)
    # up
    [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m5m6[ickg.name]['UP'][0],
                                           pdict_m5m6[ickd.name]['O'][0],
                                           pdict_m5m6[ickg.name]['UP'][0][0], rg_m4m5)
    # ckgen to sl route
    # saopb/saomb
    [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m5m6[ickg.name]['SAOPB'][0],
                                           pdict_m5m6[isl.name]['SAOPB'][0],
                                           pdict_m5m6[ickg.name]['SAOPB'][0][0]+1, rg_m4m5)
    [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
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
                                       pdict_m5m6[isl.name]['RST'][0], xysl[1] - num_bits - 1, rg_m5m6)
    # ckg to sl route
    rh0, rv0 = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                               pdict_m5m6[ickg.name]['RST'][0], pdict_m5m6[isl.name]['RST'][0], rg_m5m6)
    # zp
    yoffset=num_bits
    for i in range(num_bits):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[isl.name]['ZP<'+str(i)+'>'][0],
                                           pdict_m5m6[iret.name]['ZP<'+str(i)+'>'][0], xysl[1]-yoffset-i-1, rg_m5m6)
    #output
    # zp/zm/zmid
    for i in range(num_bits):
        rzp0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m4m5[isl.name]['ZP<'+str(i)+'>'][0],
                            xy1=np.array([pdict_m4m5[isl.name]['ZP<'+str(i)+'>'][0][0], y_top]), gridname0=rg_m5m6)
        laygen.create_boundary_pin_form_rect(rzp0, rg_m5m6, 'ZP<'+str(num_bits-i-1)+'>', laygen.layers['pin'][5], size=6, direction='top')
        rzm0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m4m5[isl.name]['ZM<'+str(i)+'>'][0],
                            xy1=np.array([pdict_m4m5[isl.name]['ZM<'+str(i)+'>'][0][0], y_top]), gridname0=rg_m5m6)
        laygen.create_boundary_pin_form_rect(rzm0, rg_m5m6, 'ZM<'+str(num_bits-i-1)+'>', laygen.layers['pin'][5], size=6, direction='top')
        rzmid0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m4m5[isl.name]['ZMID<'+str(i)+'>'][0],
                            xy1=np.array([pdict_m4m5[isl.name]['ZMID<'+str(i)+'>'][0][0], y_top]), gridname0=rg_m5m6)
        laygen.create_boundary_pin_form_rect(rzmid0, rg_m5m6, 'ZMID<'+str(num_bits-i-1)+'>', laygen.layers['pin'][5], size=6, direction='top')
        #laygen.pin(name='ZP<'+str(num_bits-i-1)+'>', layer=laygen.layers['pin'][5],
        #           xy=pdict_m4m5[isl.name]['ZP<'+str(i)+'>'], gridname=rg_m4m5)
        #laygen.pin(name='ZM<'+str(num_bits-i-1)+'>', layer=laygen.layers['pin'][5],
        #           xy=pdict_m4m5[isl.name]['ZM<'+str(i)+'>'], gridname=rg_m4m5)
        #laygen.pin(name='ZMID<'+str(num_bits-i-1)+'>', layer=laygen.layers['pin'][5],
        #           xy=pdict_m4m5[isl.name]['ZMID<'+str(i)+'>'], gridname=rg_m4m5)
    # ckdsel
    for i in range(4):
        laygen.pin(name='CKDSEL<' + str(i) + '>', layer=laygen.layers['pin'][4],
                   xy=pdict_m4m5[ickd.name]['SEL<' + str(i) + '>'], gridname=rg_m4m5)
    # extclk, extsel_clk
    laygen.pin(name='EXTCLK', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['EXTCLK'], gridname=rg_m4m5)
    laygen.pin(name='EXTSEL_CLK', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['EXTSEL_CLK'], gridname=rg_m4m5)
    # adcout
    for i in range(num_bits):
        laygen.pin(name='ADCOUT<'+str(i)+'>', layer=laygen.layers['pin'][5],
                   xy=pdict_m4m5[iret.name]['ADCOUT<'+str(i)+'>'], gridname=rg_m4m5)
    #rst
    laygen.create_boundary_pin_form_rect(rrst0, rg_m5m6, 'RST', laygen.layers['pin'][5], size=6, direction='bottom')
    # probe outputs
    laygen.pin(name='COMPOUT', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['COMPOUT'], gridname=rg_m4m5)
    laygen.pin(name='UP', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['UP'], gridname=rg_m4m5)
    laygen.pin(name='DONE', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['DONE'], gridname=rg_m4m5)
    laygen.pin(name='SARCLK', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['CLKO'], gridname=rg_m4m5)
    for i in range(num_bits):
        laygen.pin(name='SB<' + str(i) + '>', layer=laygen.layers['pin'][5],
                   xy=pdict_m5m6[isl.name]['SB<' + str(i) + '>'], gridname=rg_m5m6)
    # vdd/vss
    i=0
    for p in pdict_m3m4[iret.name]:
        if p.startswith('VDD'):
            laygen.pin(name='VDD' + str(i), layer=laygen.layers['pin'][3],
                       xy=pdict_m3m4[iret.name][p], gridname=rg_m3m4)
            i+=1
    i=0
    for p in pdict_m3m4[iret.name]:
        if p.startswith('VSS'):
            laygen.pin(name='VSS' + str(i), layer=laygen.layers['pin'][3],
                       xy=pdict_m3m4[iret.name][p], gridname=rg_m3m4)
            i+=1

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
    #capdrv generation
    cellname='sarabe'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarabe(laygen, objectname_pfix='CA0', workinglib=workinglib,
                    placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m4m5=rg_m4m5,
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
