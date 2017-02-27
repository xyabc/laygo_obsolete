# -*- coding: utf-8 -*-

import pprint

import bag
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'capdac'
impl_lib = 'adc_sar_generated'
params = dict(
    num_bit = 8,
    c_m = 1,
    rdx_array = [1, 2, 4, 8, 16, 32, 64, 128],
    )
load_from_file=True

load_from_file=True
yamlfile_system_input="adc_sar_dsn_system_input.yaml"

if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict_i = yaml.load(stream)
    params['num_bit']=sysdict_i['n_bit']-1
    params['c_m']=sysdict_i['c_m']
    params['rdx_array']=sysdict_i['rdx_array']
    #cell_name='capdac_'+str(sysdict_i['n_bit']-1)+'b'

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

