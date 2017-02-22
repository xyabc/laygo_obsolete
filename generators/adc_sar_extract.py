# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'sar_9b'
impl_lib = 'adc_sar_generated'
load_from_file=True
yamlfile_system_input="adc_sar_dsn_system_input.yaml"
if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict_i = yaml.load(stream)
    cell_name='sar_'+str(sysdict_i['n_bit'])+'b'

print('creating BAG project')
prj = bag.BagProject()

# run rcx
print('running rcx')
rcx_passed, rcx_log = prj.run_rcx(impl_lib, cell_name)
if not rcx_passed:
    raise Exception('oops rcx died.  See RCX log file %s' % rcx_log)
print('rcx passed')
