# -*- coding: utf-8 -*-

import pprint

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

import bag
import bag.tech.mos

import yaml

load_from_file=True
yamlfile_system_input="adc_sar_dsn_system_input.yaml"
yamlfile_system_output="adc_sar_dsn_system_output.yaml"
yamlfile_output="adc_sar_capdrv_nsw_array_output.yaml"

#spec
if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict = yaml.load(stream)
    with open(yamlfile_system_output, 'r') as stream:
        sysdict_o = yaml.load(stream)
    n_bit=sysdict['n_bit']
    vh=sysdict['v_in']
    vl=0
    vcm=sysdict['v_in']/2
    trf=12e-12
    vdd=sysdict['vdd']
    c0=sysdict['c_unit']*sysdict['rdx_array'][0]
    c1=sysdict['c_unit']*sysdict['rdx_array'][1]
    c2=sysdict['c_unit']*sysdict['rdx_array'][2]
    c3=sysdict['c_unit']*sysdict['rdx_array'][3]
    c4=sysdict['c_unit']*sysdict['rdx_array'][4]
    c5=sysdict['c_unit']*sysdict['rdx_array'][5]
    c6=sysdict['c_unit']*sysdict['rdx_array'][6]
    c7=sysdict['c_unit']*sysdict['rdx_array'][7]
    c_list=[c0, c1, c2, c3, c4, c5, c6, c7]
    t_dac=sysdict_o['t_dac']
else:
    n_bit=9
    vh=0.3
    vl=0.0
    vcm=0.15
    trf=10e-12
    vdd=0.8
    c0=0.2e-15
    c1=0.4e-15
    c2=0.8e-15
    c3=1.6e-15
    c4=3.2e-15
    c5=6.4e-15
    c6=12.8e-15
    c7=25.6e-15
    c_list=[c0, c1, c2, c3, c4, c5, c6, c7]
    t_dac=40e-12

pmos_type='pch'
nmos_type='nch'
#env_list = ['tt', 'ff', 'ss', 'sf', 'fs', 'ff_hot', 'ss_hot']
env_list = ['tt']
l = 16e-9
intent = 'ulvt'
pw = 4
nw = 4

mos_config = bag.BagProject().tech_info.tech_params['mos']
root_dir = mos_config['mos_char_root']
pmos_db = bag.tech.mos.MosCharDB(root_dir, pmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')
nmos_db = bag.tech.mos.MosCharDB(root_dir, nmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')

#multiplier
m_sw = [2, 4, 8]
m_min = 2
#switch transistor
vbs = -vcm
vgs = vdd-vh
vds = vh-vcm
msw=nmos_db.query(w=nw, vbs=vbs, vgs=vgs, vds=vds)

m_list=[int(m_sw[-1]) for i in range(n_bit-1)]
for j in range(len(m_list)):
    for i in range(len(m_sw)):
        #msb timing calculation
        #tsettle=c7/msw['gds']*2.3/ms
        #print('tsettle:',tsettle)
        tsettle=c_list[j]/msw['ids']*3*(vh-vcm)/m_sw[len(m_sw)-1-i]
        print('bit',j,'m_sw:',m_sw[len(m_sw)-1-i],'tsettle:',tsettle, 't_dac:',t_dac)
        if tsettle<t_dac:
            m_list[j]=int(m_sw[len(m_sw)-1-i])
print(m_list) 

#write to file
outdict=dict()
outdict['m_list']=m_list
with open(yamlfile_output, 'w') as stream:
    yaml.dump(outdict, stream)
