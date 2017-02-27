# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sarabe_9b'
impl_lib = 'adc_sar_generated'

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m_ckgen=2, 
    m_ckdly=1, 
    m_logic=1, 
    m_fsm=1, 
    m_ret=2, 
    fo_ret=2, 
    device_intent='fast',
    )
load_from_file=True

yamlfile_system_input="adc_sar_dsn_system_input.yaml"
if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict_i = yaml.load(stream)
    cell_name = 'sarabe_dualdelay_'+str(sysdict_i['n_bit'])+'b'
    params['m_ckgen']=sysdict_i['m_sarclkgen']
    params['m_logic']=sysdict_i['m_sarlogic']
    params['m_fsm']=sysdict_i['m_sarfsm']
    params['m_ret']=sysdict_i['m_sarret']
    params['fo_ret']=sysdict_i['fo_sarret']

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

