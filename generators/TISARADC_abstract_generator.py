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

"""TIADC abstract layout generator
"""
import laygo
import numpy as np
from math import log
import yaml
import os

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
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m6m7 = 'route_M6_M7_basic'

    mycell_list = []
    num_bits=9
    num_slices=8
    #load from preset
    load_from_file=True
    yamlfile_system_input="adc_sar_dsn_system_input.yaml"
    if load_from_file==True:
        with open(yamlfile_system_input, 'r') as stream:
            sysdict_i = yaml.load(stream)
        num_bits=sysdict_i['n_bit']

    #abstract generation
    cellname='TISARADC'
    sar_name = 'sar_'+str(num_bits)+'b'
    sar_pins=laygen.templates.templates[workinglib][sar_name].pins
    sar_xy=laygen.templates.get_template(templatename=sar_name, libname=workinglib).size + \
           2*laygen.templates.get_template(templatename='tap', libname=logictemplib).size + \
           np.array([0, 2])*laygen.templates.get_template(templatename=sar_name, libname=workinglib).size 
           #power line, frontend; will be removed
    print('sar_xy:', sar_xy)

    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    
    #boundary (including clocking margins)
    top_xy=sar_xy*np.array([num_slices+3, 1])
    laygen.add_rect(None, np.array([[0, 0], top_xy]), ['prBoundary', 'boundary'])

    #adc pins
    adc_pin_list=['ADCOUT<'+str(i)+'>' for i in range(num_bits)] + \
                 ['CKDSEL<'+str(i)+'>' for i in range(4)] + \
                 ['EXTCLK', 'EXTSEL_CLK']
    for i in range(num_slices):
        sar_slice_xy=sar_xy*np.array([i+1, 0])
        for pn in adc_pin_list:
            pin_xy=sar_slice_xy+sar_pins[pn]['xy']
            if pn[-1]=='>': #array
                pn_head, pn_tail = pn.split('<')
                pn_tail='<'+pn_tail
                laygen.add_pin(None, pn_head+str(i)+pn_tail, pin_xy, ['M5', 'drawing'])
            else:
                laygen.add_pin(None, pn+str(i), pin_xy, ['M5', 'drawing'])
    #clock pins
    clock_pin_list=['PHISEL<'+str(i)+'>' for i in range(4)] + \
                   ['CLKOUT_DES1', 'CLKOUT_DES2', 'CLKOUT_DSP', 'CLKRST'] #CLKRST from outside?
    clock_pin_xy_list=[i+1 for i in range(4)] + \
                      [6, 7, 8, 9]
    clock_pin_width=0.04
    sar_slice_xy=sar_xy*np.array([num_slices+1, 0])
    for i, pn in enumerate(clock_pin_list):
        #pin_xy=sar_slice_xy+sar_pins[pn]['xy']
        pin_xy=sar_slice_xy+np.array([clock_pin_xy_list[i], 0])
        pin_xy=np.array([pin_xy-np.array([clock_pin_width/2,0]),pin_xy+np.array([clock_pin_width/2,clock_pin_width*6])])
        laygen.add_pin(None, pn, pin_xy, ['M5', 'drawing'])
    #pwr pins
    pwr_pin_res=np.array([1.62, 20])
    pwr_pin_width=0.36
    for i in range(2, int(top_xy[0]/pwr_pin_res[0])-2):
        if i%2==0: pwr_pin_name='VDD'
        else: pwr_pin_name='VSS'
        pwr_rect_xy=np.array([[pwr_pin_res[0]-pwr_pin_width/2, 0], [pwr_pin_res[0]+pwr_pin_width/2, pwr_pin_res[1]]]) + \
                    np.array([pwr_pin_res*np.array([i, 0]), pwr_pin_res*np.array([i, 0])])
        laygen.add_rect(None, pwr_rect_xy, ['M7', 'drawing'])
        #pwr_pin_rect_xy=np.array([[pwr_pin_res[0]-pwr_pin_width/2, 0], [pwr_pin_res[0]+pwr_pin_width/2, 8*pwr_pin_width]]) + \
        #            np.array([pwr_pin_res*np.array([i, 0]), pwr_pin_res*np.array([i, 0])])
        pwr_pin_rect_xy=pwr_rect_xy
        laygen.add_pin(None, pwr_pin_name, pwr_pin_rect_xy, ['M7', 'pin'])

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
def generate_sar(laygen, objectname_pfix, workinglib, sarabe_name, sarafe_name, 
                 placement_grid,
                 routing_grid_m3m4, routing_grid_m4m5, routing_grid_m5m6, num_bits=8, origin=np.array([0, 0])):
    """generate sar backend """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m5m6 = routing_grid_m5m6

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
    pdict_m4m5 = laygen.get_inst_pin_coord(None, None, rg_m4m5)
    pdict_m5m6 = laygen.get_inst_pin_coord(None, None, rg_m5m6)

    #zp/zm/zmid route
    x0=pdict_m5m6[iafe.name]['ENL0<0>'][0][0]+8
    y0=pdict_m5m6[iabe.name]['ZP<0>'][1][1]
    for i in range(1, num_bits):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[iabe.name]['ZP<'+str(i)+'>'][0],
                                           np.array([x0+3*i+2, y0]),
                                           y0+i-3*num_bits, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[iabe.name]['ZM<'+str(i)+'>'][0],
                                           np.array([x0+3*i+1, y0]),
                                           y0+i-2*num_bits, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[iabe.name]['ZMID<'+str(i)+'>'][0],
                                           np.array([x0+3*i+0, y0]),
                                           y0+i-1*num_bits, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+2, y0]),
                                           pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<0>'][0],
                                           y0+i+0*num_bits+2, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+2, y0]),
                                           pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<2>'][0],
                                           y0+i+0*num_bits+2, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+1, y0]),
                                           pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<2>'][0],
                                           y0+i+1*num_bits+2, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i+1, y0]),
                                           pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<0>'][0],
                                           y0+i+1*num_bits+2, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i, y0]),
                                           pdict_m5m6[iafe.name]['ENL'+str(i-1)+'<1>'][0],
                                           y0+i+2*num_bits+2, rg_m5m6)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           np.array([x0+3*i, y0]),
                                           pdict_m5m6[iafe.name]['ENR'+str(i-1)+'<1>'][0],
                                           y0+i+2*num_bits+2, rg_m5m6)
    #saop/saom route
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iabe.name]['SAOPB'][0], pdict_m5m6[iafe.name]['OUTM'][0],
                                       pdict_m5m6[iabe.name]['SAOPB'][0][1] + 8 + 4 * num_bits, rg_m5m6)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iabe.name]['SAOMB'][0], pdict_m5m6[iafe.name]['OUTP'][0],
                                       pdict_m5m6[iabe.name]['SAOMB'][0][1] + 8 + 4 * num_bits + 1, rg_m5m6)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                       pdict_m5m6[iabe.name]['SARCLKB'][0], pdict_m5m6[iafe.name]['CLKB'][0],
                                       pdict_m5m6[iabe.name]['SARCLKB'][0][1] + 8 + 4 * num_bits - 2, rg_m5m6)
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
    #extclk/extclksel
    laygen.pin(name='EXTCLK', layer=laygen.layers['pin'][4], xy=pdict_m4m5[iabe.name]['EXTCLK'], gridname=rg_m4m5)
    laygen.pin(name='EXTSEL_CLK', layer=laygen.layers['pin'][4], xy=pdict_m4m5[iabe.name]['EXTSEL_CLK'], gridname=rg_m4m5)
    #ckdsel
    for i in range(4):
        laygen.pin(name='CKDSEL<' + str(i) + '>', layer=laygen.layers['pin'][4],
                   xy=pdict_m4m5[iabe.name]['CKDSEL<' + str(i) + '>'], gridname=rg_m4m5)
'''
