# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml

lib_name = 'adc_ec_templates'
cell_name = 'sampler_nmos'
impl_lib = 'adc_sar_generated'
tb_lib = 'adc_sar_testbenches'
tb_cell_ac = 'sampler_nmos_tb_ac'
tb_cell_noise = 'sampler_nmos_tb_noise'

#spec
cload=20e-15
vicm=0.4
vdd=0.8

load_from_file=True
verify_lvs = False
extracted = False
verify_ac = True
verify_noise = False
'''
yamlfile_system_input="adc_sar_dsn_system_input.yaml"
yamlfile_system_output="adc_sar_dsn_system_output.yaml"

if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict_i = yaml.load(stream)
    with open(yamlfile_system_output, 'r') as stream:
        sysdict_o = yaml.load(stream)
    #vamp_tran=sysdict_o['v_bit']/2
    #vamp_noise=sysdict_o['v_comp_noise']/2
'''

print('creating BAG project')
prj = bag.BagProject()

#lvs
if verify_lvs==True:
    # run lvs
    print('running lvs')
    lvs_passed, lvs_log = prj.run_lvs(impl_lib, cell_name)
    if not lvs_passed:
        raise Exception('oops lvs died.  See LVS log file %s' % lvs_log)
    print('lvs passed')

# ac test
if verify_ac==True:
    #ac test
    print('creating testbench %s__%s' % (impl_lib, tb_cell_ac))
    tb = prj.create_testbench(tb_lib, tb_cell_ac, impl_lib, cell_name, impl_lib)
    tb.set_parameter('vdd', vdd)
    tb.set_parameter('vicm', vicm)

    tb.set_simulation_environments(['tt'])

    if extracted:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')
        tb.set_simulation_view(impl_lib, 'capdac', 'calibre')

    tb.update_testbench()
    '''
    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)

    print('bw:'+str(results['bw']))
    '''

# transient noise test
if verify_noise==True:
    print('creating testbench %s__%s' % (impl_lib, tb_noise_cell))
    tb_noise = prj.create_testbench(tb_lib, tb_noise_cell, impl_lib, cell_name, impl_lib)
    tb_noise.set_parameter('cload', cload)
    tb_noise.set_parameter('vamp', vamp_noise)

    tb_noise.set_simulation_environments(['tt'])

    if extracted:
        #tb_noise.set_simulation_view(impl_lib, cell_name, 'calibre')
        tb_noise.set_simulation_view(impl_lib, 'capdac', 'calibre')

    tb_noise.update_testbench()

    print('running simulation')
    tb_noise.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb_noise.save_dir)
    print('0/1 ratio (0.841 for 1sigma):'+str(results['zero_one_ratio']))
