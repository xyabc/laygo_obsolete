# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'capdrv_nsw_array_8b'
impl_lib = 'adc_sar_generated'

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m_list=[2,2,2,2,2,2,4,8],
    device_intent='fast',
    )
load_from_file=True

yamlfile_system_input="adc_sar_dsn_system_input.yaml"
yamlfile_size="adc_sar_capdrv_nsw_array_output.yaml"
if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict_i = yaml.load(stream)
    cell_name='capdrv_nsw_array_'+str(sysdict_i['n_bit']-1)+'b'
    with open(yamlfile_size, 'r') as stream:
        sizedict = yaml.load(stream)
    params['m_list']=sizedict['m_list']

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

