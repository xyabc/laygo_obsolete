# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sarabe'
impl_lib = 'adc_sar_generated'
#tb_lib = 'adc_sar_testbenches'
#tb_cell = 'sarafe_tb_tran'

params = dict(
    lch=30e-9,
    pw=240e-9,
    nw=220e-9,
    m_ckgen=2, 
    m_ckdly=1, 
    m_logic=1, 
    m_fsm=1, 
    m_ret=1, 
    device_intent='fast2',
    )
#generate_layout = False
#extract_layout = False

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

