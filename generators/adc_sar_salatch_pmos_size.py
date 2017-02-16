# -*- coding: utf-8 -*-

import pprint

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

import bag
import bag.tech.mos

pmos_type='pch'
nmos_type='nch'
#env_list = ['tt', 'ff', 'ss', 'sf', 'fs', 'ff_hot', 'ss_hot']
env_list = ['tt']
l = 16e-9
intent = 'ulvt'
pw = 4
nw = 4
cl = 20e-15

vdd = 0.8
vincm = 0.2
vth = 0.3
vn_in = 0.001 #input noise stddev
gamma = 1 

mos_config = bag.BagProject().tech_info.tech_params['mos']
root_dir = mos_config['mos_char_root']
pmos_db = bag.tech.mos.MosCharDB(root_dir, pmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')
nmos_db = bag.tech.mos.MosCharDB(root_dir, nmos_type, ['intent', 'l'],
                                 env_list, intent=intent, l=l,
                                 method='spline')

#multiplier
m = 8*2
m_sa = m
m_in = int(m_sa/2)
m_clkh = m_in
m_rstn = 1*2
m_buf=max(int(m_in-4*2), 1*2)
m_rgnn = m_in-2*m_rstn-m_buf
m_rgnp = m_rgnn+2*m_rstn-1*2
# clkh transistor
vbs = 0.0
vgs = -vdd
vds = -vdd/2
mclkh=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)
# input transistor
vbs = 0.0
vgs = vincm-vdd
vds = vth-vdd
min0=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)
# regen_p transistor
vbs = 0.0
vgs = -vdd/2
vds = -vdd/2
mrgnp=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)
# regen_n transistor
vbs = 0.0
vgs = vdd/2
vds = vdd/2
mrgnn=nmos_db.query(w=nw, vbs=vbs, vgs=vgs, vds=vds)
# buf_n transistor
vbs = 0.0
vgs = vdd
vds = vdd/2
mbufn=nmos_db.query(w=nw, vbs=vbs, vgs=vgs, vds=vds)
# buf_p transistor
vbs = 0.0
vgs = -vdd
vds = -vdd/2
mbufp=pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds)

#timing calculation
# turn on time
c=min0['cgs']*m_in+mclkh['cdb']*m_clkh
ton=-c/mclkh['ids']/m_clkh*vth
print('ton:',ton)
# integration time
c0=min0['cdb']*m_in+mrgnp['cgs']*m_rgnp
c1=mrgnp['cdb']*m_rgnp+mrgnn['cdb']*m_rgnn+mbufn['cgs']*m_buf+mbufp['cgs']*m_buf
tint=-c0/mclkh['ids']/m_clkh*vth*2-c0/mclkh['ids']/m_clkh*vth
print('tint:',tint)
# regeneration time
c=mrgnp['cdb']*m_rgnp+mrgnn['cdb']*m_rgnn+mbufn['cgs']*m_buf+mbufp['cgs']*m_buf
trgn=c/mrgnn['gm']/m_rgnn
print('trgn:',trgn)
# buffer delay
c=cl+mbufn['cdb']*m_buf+mbufp['cdb']*m_buf
tbuf=c/mbufn['ids']/m_buf*vdd/2
print('tbuf:',tbuf)
tckq=ton+tint+trgn+tbuf
print('tckq:',tckq)
#pprint.pprint(pmos_db.query(w=pw, vbs=vbs, vgs=vgs, vds=vds))

#noise calculation
kt=1.38*10e-23*300
vn_in_tot = (kt/gamma/(min0['gm']*m_in)**3*min0['gds']*c1/(tint**2)+vn_in**2)**0.5
print('vnin:',vn_in_tot)

#vbs = 0.0
#vgs = -0.4
#vds = -0.4
#pprint.pprint(nmos_db.query(w=w, vbs=vbs, vgs=vgs, vds=vds))

