# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
from adc_sar_templates_layout_generator import *
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sarretlice'
impl_lib = 'adc_sar_generated'

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m=2,
    fo=2,
    device_intent='fast',
    )

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

