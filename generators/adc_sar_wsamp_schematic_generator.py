# -*- coding: utf-8 -*-

import pprint

import bag
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sar_wsamp_9b'
impl_lib = 'adc_sar_generated'

params = dict(
    sar_lch=16e-9,
    sar_pw=4,
    sar_nw=4,
    sar_m_sa=8,
    sar_m_drv_list=[2,2,2,2,2,2,4,8],
    sar_m_ckgen=2, 
    sar_m_ckdly=1, 
    sar_m_logic=1, 
    sar_m_fsm=1, 
    sar_m_ret=2, 
    sar_fo_ret=2, 
    sar_device_intent='fast',
    samp_lch=16e-9,
    samp_wp=6,
    samp_wn=6,
    samp_fgn=20,
    samp_fg_inbuf_list=[(10, 10), (20, 20)],
    samp_fg_outbuf_list=[(4, 4), (24, 24)],
    samp_nduml=4,
    samp_ndumr=6,
    samp_nsep=2,
    samp_intent='ulvt',
)
load_from_file=True

yamlfile_system_input="adc_sar_dsn_system_input.yaml"
yamlfile_capdrv_nsw_array_output="adc_sar_capdrv_nsw_array_output.yaml"
if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict_i = yaml.load(stream)
    with open(yamlfile_capdrv_nsw_array_output, 'r') as stream:
        capdrvdict_o = yaml.load(stream)
    cell_name = 'sar_wsamp_'+str(sysdict_i['n_bit'])+'b'
    params['sar_m_sa']=sysdict_i['m_salatch']
    params['sar_m_drv_list']=capdrvdict_o['m_list']
    params['sar_m_logic']=sysdict_i['m_sarlogic']
    params['sar_m_fsm']=sysdict_i['m_sarfsm']
    params['sar_m_ret']=sysdict_i['m_sarret']
    params['sar_fo_ret']=sysdict_i['fo_sarret']
    params['sar_m_ckgen']=sysdict_i['m_sarclkgen']

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

