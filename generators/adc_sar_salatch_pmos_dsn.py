# -*- coding: utf-8 -*-
############################################# 
# Title: ADC salatch design script
# Author: Jaeduk Han (jdhan@eecs.berkeley.edu) 
# Created(YYYYMMDD): 20170219
# Last updated: 
#############################################  

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'salatch_pmos'
impl_lib = 'adc_sar_generated'
tb_lib = 'adc_sar_testbenches'
tb_cell = 'salatch_pmos_tb_tran'
tb_noise_cell = 'salatch_pmos_tb_trannoise'

#spec
cload=20e-15
vamp_tran=1e-3
vamp_noise=2e-3

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m=8, #larger than 8, even number
    device_intent='fast',
    )
generate_layout = False
extract_layout = False
verify = False
verify_noise = False

print('creating BAG project')
prj = bag.BagProject()

# create design module and run design method.
print('designing module')
dsn = prj.create_design_module(lib_name, cell_name)
print('design parameters:\n%s' % pprint.pformat(params))
dsn.design(**params)

# implement the design
print('implementing design with library %s' % impl_lib)
dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)

