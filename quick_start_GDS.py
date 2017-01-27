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

"""Quick start for gds flow - nand generator"""
import laygo
import numpy as np
#initialize
laygen = laygo.GridLayoutGenerator(config_file="./labs/laygo_config.yaml")
laygen.use_phantom = True #for abstract generation. False when generating real cells.
utemplib = 'laygo10n_microtemplates_dense' #device template library name
laygen.load_template(filename='./labs/'+utemplib+'_templates.yaml', libname=utemplib)
laygen.load_grid(filename='./labs/'+utemplib+'_grids.yaml', libname=utemplib)
laygen.templates.sel_library(utemplib)
laygen.grids.sel_library(utemplib)
# library
workinglib = 'laygo_test'
laygen.add_library(workinglib)
laygen.sel_library(workinglib)
# grids
pg = 'placement_basic'  # placement grid
rg_m1m2 = 'route_M1_M2_cmos'
rg_m2m3 = 'route_M2_M3_cmos'
rg_m1m2_pin = 'route_M1_M2_basic'
rg_m2m3_pin = 'route_M2_M3_basic'
# cell generation
laygen.add_cell('nand_test')
laygen.sel_cell('nand_test')
# cell placements
m=2 #sizing parameter: nf/2
in0 = laygen.place(None, 'nmos4_fast_boundary', pg, xy=[0, 0])
in1 = laygen.relplace(None, 'nmos4_fast_center_nf2', pg, in0.name, shape=[m, 1])
in2 = laygen.relplace(None, 'nmos4_fast_boundary', pg, in1.name)
in3 = laygen.relplace(None, 'nmos4_fast_boundary', pg, in2.name)
in4 = laygen.relplace(None, 'nmos4_fast_center_nf2', pg, in3.name, shape=[m, 1])
in5 = laygen.relplace(None, 'nmos4_fast_boundary', pg, in4.name)
ip0 = laygen.relplace(None, 'pmos4_fast_boundary', pg, in0.name, direction='top', transform='MX')
ip1 = laygen.relplace(None, 'pmos4_fast_center_nf2', pg, ip0.name, transform='MX', shape=[m, 1])
ip2 = laygen.relplace(None, 'pmos4_fast_boundary', pg, ip1.name, transform='MX')
ip3 = laygen.relplace(None, 'pmos4_fast_boundary', pg, ip2.name, transform='MX')
ip4 = laygen.relplace(None, 'pmos4_fast_center_nf2', pg, ip3.name, transform='MX', shape=[m, 1])
ip5 = laygen.relplace(None, 'pmos4_fast_boundary', pg, ip4.name, transform='MX')
#a
for i in range(m):
    laygen.route(None, laygen.layers['metal'][1], xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2,
                 refinstname0=in4.name, refpinname0='G0', refinstindex0=[i, 0], addvia0=True,
                 refinstname1=ip4.name, refpinname1='G0', refinstindex1=[i, 0])
laygen.route(None, laygen.layers['metal'][2], xy0=[-2, 0], xy1=[0, 0], gridname0=rg_m1m2,
             refinstname0=ip4.name, refpinname0='G0', refinstindex0=[0, 0],
             refinstname1=ip4.name, refpinname1='G0', refinstindex1=[m - 1, 0])
ra0 = laygen.route(None, laygen.layers['metal'][3], xy0=[0, 0], xy1=[0, 2], gridname0=rg_m2m3,
                   refinstname0=ip4.name, refpinname0='G0', refinstname1=ip4.name, refpinname1='G0', addvia0=True,
                   endstyle0="extend", endstyle1="extend")
# b
for i in range(m):
    laygen.route(None, laygen.layers['metal'][1], xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstindex0=[i, 0], addvia0=True,
                 refinstname1=ip1.name, refpinname1='G0', refinstindex1=[i, 0])
laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=[2, 0], gridname0=rg_m1m2,
             refinstname0=in1.name, refpinname0='G0', refinstindex0=[0, 0],
             refinstname1=in1.name, refpinname1='G0', refinstindex1=[m - 1, 0])
rb0 = laygen.route(None, laygen.layers['metal'][3], xy0=[0, 0], xy1=[0, 2], gridname0=rg_m2m3, refinstname0=in1.name,
                   refpinname0='G0', refinstname1=in1.name, refpinname1='G0', addvia0=True,
                   endstyle0="extend", endstyle1="extend")
#internal connections
laygen.route(None, laygen.layers['metal'][2], xy0=[0, 1], xy1=[0, 1], gridname0=rg_m2m3, refinstname0=in1.name,
             refpinname0='D0', refinstname1=in4.name, refpinname1='S1', refinstindex1=[m - 1, 0])
laygen.route(None, laygen.layers['metal'][2], xy0=[0, 1], xy1=[0, 1], gridname0=rg_m2m3, refinstname0=ip1.name,
             refpinname0='D0', refinstname1=ip4.name, refpinname1='D0', refinstindex1=[m - 1, 0])
for i in range(m):
    laygen.via(None, [0, 1], refinstname=in1.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
    laygen.via(None, [0, 1], refinstname=ip1.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
    laygen.via(None, [0, 1], refinstname=in4.name, refpinname='S0', refinstindex=[i, 0], gridname=rg_m1m2)
    laygen.via(None, [0, 1], refinstname=ip4.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
laygen.via(None, [0, 1], refinstname=in4.name, refpinname='S1', refinstindex=[m - 1, 0], gridname=rg_m1m2)
#output
laygen.route(None, laygen.layers['metal'][2], xy0=[-1, 0], xy1=[1, 0], gridname0=rg_m2m3,
             refinstname0=in4.name, refpinname0='D0', refinstindex0=[0, 0],
             refinstname1=in4.name, refpinname1='D0', refinstindex1=[m - 1, 0])
for i in range(m):
    laygen.via(None, [0, 0], refinstname=in4.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=[0, 1], gridname0=rg_m2m3,
                   refinstname0=in4.name, refpinname0='D0', refinstindex0=[m - 1, 0], addvia0 = True,
                   refinstname1=ip4.name, refpinname1='D0', refinstindex1=[m - 1, 0], addvia1 = True)
# power and ground vertical route
xy_s0 = laygen.get_template_pin_coord(in1.cellname, 'S0', rg_m1m2)[0, :]
for i in range(m + 1):
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=[i, 0], addvia0 = True,
                 refinstname1=in1.name, refinstindex1=[i, 0])
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstindex0=[i, 0], addvia0 = True,
                 refinstname1=ip1.name, refinstindex1=[i, 0])
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=ip4.name, refinstindex0=[i, 0], addvia0 = True,
                 refinstname1=ip4.name, refinstindex1=[i, 0])
# power and groud rail
xy = laygen.get_template_size(in5.cellname, rg_m1m2) * np.array([1, 0])
rvdd=laygen.route(None, laygen.layers['metal'][2], xy0=[0, 0], xy1=xy, gridname0=rg_m1m2,
                  refinstname0=ip0.name, refinstname1=ip5.name)
rvss=laygen.route(None, laygen.layers['metal'][2], xy0=[0, 0], xy1=xy, gridname0=rg_m1m2,
                  refinstname0=in0.name, refinstname1=in5.name)
# pins
laygen.pin(name='A', layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(ra0.name, rg_m2m3), gridname=rg_m2m3)
laygen.pin(name='B', layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(rb0.name, rg_m2m3), gridname=rg_m2m3)
laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(ro0.name, rg_m2m3), gridname=rg_m2m3)
laygen.pin(name='VDD', layer=laygen.layers['pin'][1], xy=laygen.get_rect_xy(rvdd.name, rg_m1m2), gridname=rg_m1m2)
laygen.pin(name='VSS', layer=laygen.layers['pin'][1], xy=laygen.get_rect_xy(rvss.name, rg_m1m2), gridname=rg_m1m2)
# export
laygen.export_GDS('output.gds', cellname='nand_test', layermapfile="./labs/laygo10n.layermap")
