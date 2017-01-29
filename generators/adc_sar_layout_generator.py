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

def generate_sar(laygen, objectname_pfix, workinglib, placement_grid,
                 routing_grid_m3m4, routing_grid_m5m6, num_bits=8, origin=np.array([0, 0])):
    """generate sar backend """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m5m6 = routing_grid_m5m6

    sarabe_name = 'sarabe'
    #space_name = 'space'
    sarafe_name = 'sarafe'

    #xy0=laygen.get_template_size(name=space_name, gridname=pg, libname=workinglib)
    #xsp=xy0[0]
    #ysp=xy0[1]

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
    pdict_m5m6 = laygen.get_inst_pin_coord(None, None, rg_m5m6)
    #x_right = laygen.get_inst_xy(name=iret.name, gridname=rg_m5m6)[0]\
    #         +laygen.get_template_size(name=iret.cellname, gridname=rg_m5m6, libname=workinglib)[0] - 1
    #y_top = laygen.get_inst_xy(name=ickg.name, gridname=rg_m5m6)[1]-1
    #xysl = laygen.get_inst_xy(name=isl.name, gridname=rg_m5m6)
    #xyret = laygen.get_inst_xy(name=iret.name, gridname=rg_m5m6)
    #xyfsm = laygen.get_inst_xy(name=ifsm.name, gridname=rg_m5m6)

    #zp/zm/zmid route
    for i in range(1, num_bits):
        if i==4: #hack for zp<4>, zm<4>
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[iabe.name]['ZP<'+str(i)+'>'][0],
                                               pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<0>'][0],
                                               pdict_m5m6[iabe.name]['ZP<' + str(i) + '>'][0][1]+6, rg_m5m6)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[iabe.name]['ZP<'+str(i)+'>'][0],
                                               pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<2>'][0],
                                               pdict_m5m6[iabe.name]['ZP<' + str(i) + '>'][0][1]+6, rg_m5m6)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[iabe.name]['ZM<'+str(i)+'>'][0],
                                               pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<2>'][0],
                                               pdict_m5m6[iabe.name]['ZM<' + str(i) + '>'][0][1]+6-1, rg_m5m6)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[iabe.name]['ZM<'+str(i)+'>'][0],
                                               pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<0>'][0],
                                               pdict_m5m6[iabe.name]['ZM<' + str(i) + '>'][0][1]+6-1, rg_m5m6)
        else:
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[iabe.name]['ZP<'+str(i)+'>'][0],
                                               pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<0>'][0],
                                               pdict_m5m6[iabe.name]['ZP<' + str(i) + '>'][0][1]+6+i, rg_m5m6)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[iabe.name]['ZP<'+str(i)+'>'][0],
                                               pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<2>'][0],
                                               pdict_m5m6[iabe.name]['ZP<' + str(i) + '>'][0][1]+6+i, rg_m5m6)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[iabe.name]['ZM<'+str(i)+'>'][0],
                                               pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<2>'][0],
                                               pdict_m5m6[iabe.name]['ZM<' + str(i) + '>'][0][1]+6+i+num_bits, rg_m5m6)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[iabe.name]['ZM<'+str(i)+'>'][0],
                                               pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<0>'][0],
                                               pdict_m5m6[iabe.name]['ZM<' + str(i) + '>'][0][1]+6+i+num_bits, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[iabe.name]['ZMID<'+str(i)+'>'][0],
                                           pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<1>'][0],
                                           pdict_m5m6[iabe.name]['ZMID<' + str(i) + '>'][0][1]+6+i+2*num_bits, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[iabe.name]['ZMID<'+str(i)+'>'][0],
                                           pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<1>'][0],
                                           pdict_m5m6[iabe.name]['ZMID<' + str(i) + '>'][0][1]+6+i+2*num_bits, rg_m5m6)
    #saop/saom route
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iabe.name]['SAOPB'][0], pdict_m5m6[iafe.name]['OUTM'][0],
                                       pdict_m5m6[iabe.name]['SAOPB'][0][1] + 6 + 4 * num_bits, rg_m5m6)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iabe.name]['SAOMB'][0], pdict_m5m6[iafe.name]['OUTP'][0],
                                       pdict_m5m6[iabe.name]['SAOMB'][0][1] + 6 + 4 * num_bits + 1, rg_m5m6)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iabe.name]['SARCLKB'][0], pdict_m5m6[iafe.name]['CLKB'][0],
                                       pdict_m5m6[iabe.name]['SARCLKB'][0][1] + 6 + 4 * num_bits, rg_m5m6)
    #VDD/VSS pin
    i=0
    for p in pdict_m3m4[iabe.name]:
        if p.startswith('VDD'):
            rvdd = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                                gridname0=rg_m3m4, refinstname0=iabe.name, refpinname0=p, refinstname1=iafe.name,
                                refpinname1='VDD0', direction='y')
            laygen.pin(name='VDD' + str(i), layer=laygen.layers['pin'][3],
                       xy=laygen.get_rect_xy(rvdd.name, rg_m3m4, sort=True), gridname=rg_m3m4, netname='VDD')
            i+=1
    i=0
    for p in pdict_m3m4[iabe.name]:
        if p.startswith('VSS'):
            rvss = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                                gridname0=rg_m3m4, refinstname0=iabe.name, refpinname0=p, refinstname1=iafe.name,
                                refpinname1='VSS0', direction='y')
            laygen.pin(name='VSS' + str(i), layer=laygen.layers['pin'][3],
                       xy=laygen.get_rect_xy(rvss.name, rg_m3m4, sort=True), gridname=rg_m3m4, netname='VSS')
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
    #vol/vor
    for i in range(num_bits-1):
        laygen.pin(name='VOL<'+str(i)+'>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iafe.name]['VOL<'+str(i)+'>'], gridname=rg_m5m6)
        laygen.pin(name='VOR<'+str(i)+'>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iafe.name]['VOR<'+str(i)+'>'], gridname=rg_m5m6)
    #adcout
    for i in range(num_bits):
        laygen.pin(name='ADCOUT<'+str(i)+'>', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iabe.name]['ADCOUT<'+str(i)+'>'], gridname=rg_m5m6)
    #clk
    laygen.pin(name='CLK', layer=laygen.layers['pin'][5], xy=pdict_m5m6[iabe.name]['RST'], gridname=rg_m5m6)

    '''
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
                                       pdict_m5m6[isl.name]['RST'][0], xysl[1] - num_bits - 1, rg_m5m6)
    # ckg to sl route
    rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                               pdict_m4m5[ickg.name]['RST'][0], pdict_m4m5[isl.name]['RST'][0], rg_m4m5)
    # zp
    #yoffset=num_bits
    for i in range(num_bits):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[isl.name]['ZP<'+str(i)+'>'][0],
                                           pdict_m5m6[iret.name]['ZP<'+str(i)+'>'][0], xysl[1]+i+3, rg_m5m6)
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
    # SAOPB/SAOMB
    laygen.create_boundary_pin_form_rect(rsaopb0, rg_m4m5, 'SAOPB', laygen.layers['pin'][5], size=6, direction='top')
    laygen.create_boundary_pin_form_rect(rsaomb0, rg_m4m5, 'SAOMB', laygen.layers['pin'][5], size=6, direction='top')
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
    laygen.pin(name='SARCLKB', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['CLKOB'], gridname=rg_m4m5)
    for i in range(num_bits):
        laygen.pin(name='SB<' + str(i) + '>', layer=laygen.layers['pin'][5],
                   xy=pdict_m5m6[isl.name]['SB<' + str(i) + '>'], gridname=rg_m5m6)
    # vdd/vss
    i=0
    for p in pdict_m3m4[iret.name]:
        if p.startswith('VDD'):
            laygen.pin(name='VDD' + str(i), layer=laygen.layers['pin'][3],
                       xy=pdict_m3m4[iret.name][p], gridname=rg_m3m4, netname='VDD')
            i+=1
    i=0
    for p in pdict_m3m4[iret.name]:
        if p.startswith('VSS'):
            laygen.pin(name='VSS' + str(i), layer=laygen.layers['pin'][3],
                       xy=pdict_m3m4[iret.name][p], gridname=rg_m3m4, netname='VSS')
            i+=1
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
    cellname='sar'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sar(laygen, objectname_pfix='SA0', workinglib=workinglib,
                 placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m5m6=rg_m5m6,
                 num_bits=8, origin=np.array([0, 0]))
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
