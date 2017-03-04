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

"""GridBasedLayoutGenerator utility functions for users"""
__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

#import struct
#import math
#from math import *
import numpy as np
from copy import deepcopy

def generate_power_rails(laygen, routename_tag, layer, gridname, netnames=['VDD', 'VSS'], direction='x', 
                         start_index=0, end_index=0, route_index=None, via_index=None, generate_pin=True): 
    """generate power rails"""
    rail_list=[]
    for netidx, netname in enumerate(netnames):
        rail_sub_list=[]
        for rcnt, ridx in enumerate(route_index[netidx]):
            if direction=='x': rxy0=np.array([[start_index, ridx], [end_index, ridx]])  
            if direction=='y': rxy0=np.array([[ridx, start_index], [ridx, end_index]])  
            if generate_pin == True:
                p=laygen.pin(name=netname + routename_tag + str(rcnt), layer=layer, xy=rxy0, gridname=gridname, netname=netname)
                rail_sub_list.append(p)
            else:
                r=laygen.route(None, layer, xy0=rxy0[0], xy1=rxy0[1], gridname0=gridname)
                rail_sub_list.append(r)
            if not via_index==None: #via generation
                for vidx in via_index[netidx]:
                    if direction=='x': vxy0=np.array([vidx, ridx])
                    else: vxy0=np.array([ridx, vidx])
                    laygen.via(None, vxy0, gridname=gridname)
        rail_list.append(rail_sub_list)
    return rail_list

def generate_power_rails_from_rails_xy(laygen, routename_tag, layer, gridname, netnames=['VDD', 'VSS'], direction='x', 
                                       input_rails_xy=None, generate_pin=True, 
                                       overwrite_start_coord=None, overwrite_end_coord=None, 
                                       offset_route_start=0, offset_route_end=0):
    """generate power rails from pre-existing power rails in upper/lower layer. 
       the pre-existing rail information is provided as xy array
    """
    route_index=[]
    via_index=[]
    for netidx, netname in enumerate(netnames):
        sub_via_index=[]
        for i, irxy in enumerate(input_rails_xy[netidx]):   
            if direction == 'x':
                #boundary estimation
                if netidx==0 and i==0: #initialize
                    start_index=irxy[0][0]
                    end_index=irxy[0][0]
                    route_index_start=min((irxy[0][1], irxy[1][1]))
                    route_index_end=max((irxy[0][1], irxy[1][1]))
                else:
                    if start_index > irxy[0][0]: start_index=irxy[0][0]
                    if end_index < irxy[0][0]: end_index=irxy[0][0]
                    rist=min((irxy[0][1], irxy[1][1]))
                    ried=max((irxy[0][1], irxy[1][1]))
                    if route_index_start < rist: route_index_start = rist
                    if route_index_end > ried: route_index_end = ried
                sub_via_index.append(irxy[0][0])
            else:
                #boundary estimation
                if netidx==0 and i==0: #initialize
                    start_index=irxy[0][1]
                    end_index=irxy[0][1]
                    route_index_start=min((irxy[0][0], irxy[1][0]))
                    route_index_end=max((irxy[0][0], irxy[1][0]))
                else:
                    if start_index > irxy[0][1]: start_index=irxy[0][1]
                    if end_index < irxy[0][1]: end_index=irxy[0][1]
                    rist=min((irxy[0][0], irxy[1][0]))
                    ried=max((irxy[0][0], irxy[1][0]))
                    if route_index_start < rist: route_index_start = rist
                    if route_index_end > ried: route_index_end = ried
                sub_via_index.append(irxy[0][1])
        via_index.append(np.array(sub_via_index))
    #offset 
    route_index_start+=offset_route_start
    route_index_end+=offset_route_end
    #route index
    for netidx, netname in enumerate(netnames):
        sub_route_index=[]
        for ri in range(int((route_index_end - route_index_start + 1)/len(netnames))):
            sub_route_index += [route_index_start + netidx + len(netnames)*ri]
        route_index.append(np.array(sub_route_index))
    #overwrite start/end index if necessary
    if not overwrite_start_coord==None:
        start_index=overwrite_start_coord 
    if not overwrite_end_coord==None:
        end_index=overwrite_end_coord 
    return generate_power_rails(laygen, routename_tag=routename_tag, layer=layer, gridname=gridname, netnames=netnames, direction=direction, 
                                start_index=start_index, end_index=end_index, route_index=route_index, via_index=via_index, generate_pin=generate_pin) 

def generate_power_rails_from_rails_rect(laygen, routename_tag, layer, gridname, netnames=['VDD', 'VSS'], direction='x', 
                                         input_rails_rect=None, generate_pin=True, 
                                         overwrite_start_coord=None, overwrite_end_coord=None, 
                                         offset_route_start=0, offset_route_end=0):
    """generate power rails from pre-existing power rails in upper/lower layer. 
       the pre-existing rail information is provided as rect
    """
    xy=[]
    for netidx, netname in enumerate(netnames):
        sub_xy=[]
        for i, ir in enumerate(input_rails_rect[netidx]):    
            sub_xy.append(laygen.get_rect_xy(ir.name, gridname))
        xy.append(np.array(sub_xy))
    return generate_power_rails_from_rails_xy(laygen, routename_tag, layer, gridname, netnames=netnames, direction=direction, 
                                              input_rails_xy=xy, generate_pin=generate_pin, 
                                              overwrite_start_coord=overwrite_start_coord, overwrite_end_coord=overwrite_end_coord,
                                              offset_route_start=offset_route_start, offset_route_end=offset_route_end)

def generate_power_rails_from_rails_inst(laygen, routename_tag, layer, gridname, netnames=['VDD', 'VSS'], direction='x', 
                                         input_rails_instname=None, input_rails_pin_prefix=['VDD', 'VSS'], generate_pin=True, 
                                         overwrite_start_coord=None, overwrite_end_coord=None, 
                                         offset_route_start=0, offset_route_end=0):
    """generate power rails from pre-existing power rails in upper/lower layer. 
       the pre-existing rail information is provided as inst / pin prefix
    """
    xy=[]
    pdict=laygen.get_inst_pin_coord(None, None, gridname)
    iname=input_rails_instname
    for pfix in input_rails_pin_prefix:
        sub_xy=[]
        for pn, p in pdict[iname].items():
            if pn.startswith(pfix):
                sub_xy.append(p)
        xy.append(sub_xy)
    return generate_power_rails_from_rails_xy(laygen, routename_tag, layer, gridname, netnames=netnames, direction=direction, 
                                              input_rails_xy=xy, generate_pin=generate_pin, 
                                              overwrite_start_coord=overwrite_start_coord, overwrite_end_coord=overwrite_end_coord,
                                              offset_route_start=offset_route_start, offset_route_end=offset_route_end)
'''
def generate_grids_from_xy(laygen, gridname_input, xy, gridname_output):
    """generate route grids combining a pre-existing grid and xy-array
    it will create a new array by copying the given grid and update part of entries from xy-lists
    """
    gi=laygen.get_grid(gridname_input)
    bnd=deepcopy(gi.xy)
    xgrid = deepcopy(gi.xgrid)
    ygrid = deepcopy(gi.ygrid)

    laygen.grids.add_route_grid(name=gridname_output, libname=None, xy=bnd, xgrid=xgrid, ygrid=ygrid, xwidth=xwidth,
                       ywidth=ywidth, viamap=None)
'''