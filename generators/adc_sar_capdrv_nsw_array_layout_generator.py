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

def generate_capdrv_array(laygen, objectname_pfix, templib_logic, cdrv_name_list, placement_grid, routing_grid_m2m3,
                          routing_grid_m4m5, num_bits=8, num_bits_row=4, origin=np.array([0, 0])):
    """generate cap driver array """
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m4m5 = routing_grid_m4m5
    num_row=int(num_bits/num_bits_row)

    tap_name='tap'
    #cdrv_name='capdrv_nsw'
    cdac_name='capdac_'+str(num_bits-1)+'b'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    #space cell insertion
    #1. making it fit to DAC-DAC dimension
    x0 = laygen.templates.get_template(cdac_name, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cdrv_name_list[0], libname=workinglib).xy[1][0] * num_bits_row \
         - laygen.templates.get_template(tap_name, libname=templib_logic).xy[1][0] * 2 
    m_space = int(round(x0 / laygen.templates.get_template(space_1x_name, libname=templib_logic).xy[1][0]))
    m_space = max(0, m_space)
    m_space_4x = 0
    m_space_2x = 0
    m_space_1x = m_space
    x0 = laygen.templates.get_template(tap_name, libname=templib_logic).xy[1][0] * 2 \
         + laygen.templates.get_template(cdrv_name_list[0], libname=workinglib).xy[1][0] * num_bits_row \
         + laygen.templates.get_template(space_1x_name, libname=templib_logic).xy[1][0] * m_space_1x \
         + laygen.templates.get_template(space_2x_name, libname=templib_logic).xy[1][0] * m_space_2x
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    #print(m_space, m_space_4x, m_space_2x)


    #boundaries
    m_bnd = int(x0 / laygen.templates.get_template('boundary_bottom').xy[1][0])
    devname_bnd_left = []
    devname_bnd_right = []
    transform_bnd_left = []
    transform_bnd_right = []
    for i in range(num_row):
        if i%2==0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    [bnd_bottom, bnd_top, bnd_left, bnd_right] = generate_boundary(laygen, objectname_pfix='BND0',
                                                                   placement_grid=pg,
                                                                   devname_bottom=['boundary_bottomleft',
                                                                                   'boundary_bottom',
                                                                                   'boundary_bottomright'],
                                                                   shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]),
                                                                                 np.array([1, 1])],
                                                                   devname_top=['boundary_topleft', 'boundary_top',
                                                                                'boundary_topright'],
                                                                   shape_top=[np.array([1, 1]), np.array([m_bnd, 1]),
                                                                              np.array([1, 1])],
                                                                   devname_left=devname_bnd_left,
                                                                   transform_left=transform_bnd_left,
                                                                   devname_right=devname_bnd_right,
                                                                   transform_right=transform_bnd_right,
                                                                   origin=np.array([0, 0]))
    array_origin = origin + laygen.get_inst_xy(bnd_bottom[0].name, pg) \
                   + laygen.get_template_size(bnd_bottom[0].cellname, pg)
    # placement
    itapl=[]
    icdrv=[]
    itapr=[]
    isp4x=[]
    isp2x=[]
    isp1x=[]

    for i in range(num_row):
        if i==0: 
            itapl.append(laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                                      gridname = pg, xy=array_origin, template_libname = templib_logic))
            tf='R0'
        else:
            if i%2==0: tf='R0'
            else: tf='MX'
            itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i), templatename = tap_name,
                                   gridname = pg, refinstname = itapl[-1].name, transform=tf, 
                                   direction = 'top', template_libname=templib_logic))
        refi = itapl[-1].name
        for j in range(num_bits_row): #main driver
            cdrv_name=cdrv_name_list[i*num_bits_row+j]
            icdrv.append(laygen.relplace(name = "I" + objectname_pfix + 'CDRV'+str(i)+'_'+str(j), templatename = cdrv_name,
                                   gridname = pg, refinstname = refi, transform=tf, 
                                   template_libname=workinglib))
            refi = icdrv[-1].name
        if not m_space_4x==0:
            isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X'+str(i), templatename=space_4x_name,
                         shape = np.array([m_space_4x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp4x[-1].name
        if not m_space_2x==0:
            isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X'+str(i), templatename=space_2x_name,
                         shape = np.array([m_space_2x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp2x[-1].name
        if not m_space_1x==0:
            isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X'+str(i), templatename=space_1x_name,
                         shape=np.array([m_space_1x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp1x[-1].name
        itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i), templatename = tap_name,
                               gridname = pg, refinstname = refi, transform=tf, template_libname = templib_logic))

    # internal pins
    icdrv_en0_xy=[]
    icdrv_en1_xy=[]
    icdrv_en2_xy=[]
    icdrv_vref0_xy=[]
    icdrv_vref1_xy=[]
    icdrv_vref2_xy=[]
    icdrv_vo_xy=[]
    for i in range(num_row):
        for j in range(num_bits_row):
            icdrv_en0_xy.append(laygen.get_inst_pin_coord(icdrv[i*num_bits_row+j].name, 'EN<0>', rg_m4m5))
            icdrv_en1_xy.append(laygen.get_inst_pin_coord(icdrv[i*num_bits_row+j].name, 'EN<1>', rg_m4m5))
            icdrv_en2_xy.append(laygen.get_inst_pin_coord(icdrv[i*num_bits_row+j].name, 'EN<2>', rg_m4m5))
            icdrv_vref0_xy.append(laygen.get_inst_pin_coord(icdrv[i*num_bits_row+j].name, 'VREF<0>', rg_m4m5))
            icdrv_vref1_xy.append(laygen.get_inst_pin_coord(icdrv[i*num_bits_row+j].name, 'VREF<1>', rg_m4m5))
            icdrv_vref2_xy.append(laygen.get_inst_pin_coord(icdrv[i*num_bits_row+j].name, 'VREF<2>', rg_m4m5))
            icdrv_vo_xy.append(laygen.get_inst_pin_coord(icdrv[i*num_bits_row+j].name, 'VO', rg_m4m5))

    # reference route coordinate
    x0 = icdrv_en0_xy[0][0][0]
    y0 = laygen.get_inst_xy(name=icdrv[0].name, gridname=rg_m4m5)[1]
    y1 = laygen.get_inst_xy(name=icdrv[-1].name, gridname=rg_m4m5)[1]
    if num_row%2==1:
        y1 += laygen.get_template_size(name=icdrv[-1].cellname, gridname=rg_m4m5, libname=icdrv[-1].libname)
    # vref route
    rvref0=[]
    rvref1=[]
    rvref2=[]
    for i in range(num_row):
        rvref0.append(laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m4m5,
                              refinstname0=icdrv[i*num_bits_row].name, refpinname0='VREF<0>', refinstindex0=np.array([0, 0]),
                              refinstname1=icdrv[i*num_bits_row].name, refpinname1='VREF<0>', refinstindex1=np.array([num_bits_row-1, 0])))
        rvref1.append(laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m4m5,
                              refinstname0=icdrv[i*num_bits_row].name, refpinname0='VREF<1>', refinstindex0=np.array([0, 0]),
                              refinstname1=icdrv[i*num_bits_row].name, refpinname1='VREF<1>', refinstindex1=np.array([num_bits_row-1, 0])))
        rvref2.append(laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m4m5,
                              refinstname0=icdrv[i*num_bits_row].name, refpinname0='VREF<2>', refinstindex0=np.array([0, 0]),
                              refinstname1=icdrv[i*num_bits_row].name, refpinname1='VREF<2>', refinstindex1=np.array([num_bits_row-1, 0])))
    # vref vertical route
    if not num_row==0:
        for i in range(1, num_row):
            [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], icdrv_vref0_xy[0][0], icdrv_vref0_xy[i*num_bits_row][0], x0+1, rg_m4m5)
            [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], icdrv_vref1_xy[0][0], icdrv_vref1_xy[i*num_bits_row][0], x0+2, rg_m4m5)
            [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], icdrv_vref2_xy[0][0], icdrv_vref2_xy[i*num_bits_row][0], x0+3, rg_m4m5)
    # en route
    ren0 = []
    ren1 = []
    ren2 = []
    for i in range(num_row):
        for j in range(num_bits_row):
            rh0, _ren0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                        icdrv_en0_xy[num_bits_row * i + j][0],
                                        np.array([icdrv_en0_xy[num_bits_row * i + j][0][0] + i*3 + 3, y0]), rg_m4m5)
            ren0.append(_ren0)
            rh0, _ren1 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                        icdrv_en1_xy[num_bits_row * i + j][0],
                                        np.array([icdrv_en1_xy[num_bits_row * i + j][0][0] + i*3 + 4, y0]), rg_m4m5)
            ren1.append(_ren1)
            rh0, _ren2 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                        icdrv_en2_xy[num_bits_row * i + j][0],
                                        np.array([icdrv_en2_xy[num_bits_row * i + j][0][0] + i*3 + 5, y0]), rg_m4m5)
            ren2.append(_ren2)
    # vc0 route
    rh0, rvc0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                 icdrv_vref1_xy[0][0],
                                 np.array([icdrv_en0_xy[0][0][0] + num_row*3 + 4, y1]), rg_m4m5)
                                 #np.array([icdrv_vo_xy[0][0][0] - 2 - 1, y1]), rg_m4m5)
    # vo route
    rvo = []
    for i in range(num_row):
        for j in range(num_bits_row):
            rh0, _rvo = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                        icdrv_vo_xy[num_bits_row * i + j][0],
                                        np.array([icdrv_en0_xy[num_bits_row * i + j][0][0] + num_row*3 + 6 + i, y1]), rg_m4m5)
                                        #np.array([icdrv_vo_xy[num_bits_row * i + j][0][0] + i - 2, y1]), rg_m4m5)
            rvo.append(_rvo)
    #pins
    laygen.create_boundary_pin_form_rect(rvref0[0], rg_m4m5, "VREF<0>", laygen.layers['pin'][4], size=4, direction='left')
    laygen.create_boundary_pin_form_rect(rvref1[0], rg_m4m5, "VREF<1>", laygen.layers['pin'][4], size=4, direction='left')
    laygen.create_boundary_pin_form_rect(rvref2[0], rg_m4m5, "VREF<2>", laygen.layers['pin'][4], size=4, direction='left')
    for i, _ren0 in enumerate(ren0):
        laygen.create_boundary_pin_form_rect(_ren0, rg_m4m5, "EN"+str(i)+"<0>", laygen.layers['pin'][5], size=6, direction='bottom')
    for i, _ren1 in enumerate(ren1):
        laygen.create_boundary_pin_form_rect(_ren1, rg_m4m5, "EN"+str(i)+"<1>", laygen.layers['pin'][5], size=6, direction='bottom')
    for i, _ren2 in enumerate(ren2):
        laygen.create_boundary_pin_form_rect(_ren2, rg_m4m5, "EN"+str(i)+"<2>", laygen.layers['pin'][5], size=6, direction='bottom')
    laygen.create_boundary_pin_form_rect(rvc0, rg_m4m5, "VO_C0", laygen.layers['pin'][5], size=6, direction='top', netname="VREF<1>")
    for i, _rvo in enumerate(rvo):
        laygen.create_boundary_pin_form_rect(_rvo, rg_m4m5, "VO<"+str(i)+">", laygen.layers['pin'][5], size=6, direction='top')

    # power pin
    pwr_dim=laygen.get_template_size(name=itapl[-1].cellname, gridname=rg_m2m3, libname=itapl[-1].libname)
    rvdd = []
    rvss = []
    if num_row%2==0: rp1='VSS'
    else: rp1='VDD'
    for i in range(1, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-2), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-2), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-1), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-1), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')

    for i in range(num_row):
        for j in range(1, int(pwr_dim[0]/2)):
            rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                         refinstname0=itapl[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                         refinstname1=itapl[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                         refinstname0=itapl[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapl[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))
            rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                         refinstname0=itapr[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                         refinstname1=itapr[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                         refinstname0=itapr[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapr[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))


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
    cellname='capdrv_nsw_array_8b'
    cdrv_name_list=[
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_4x',
        'capdrv_nsw_8x',
        ]
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_capdrv_array(laygen, objectname_pfix='CA0', templib_logic=logictemplib, cdrv_name_list=cdrv_name_list,
                          placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m4m5=rg_m4m5, num_bits=8,
                          num_bits_row=4, origin=np.array([0, 0]))
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
