# -*- coding: utf-8 -*-

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
vamp_noise=1e-3

extracted = False
verify_tran = True
verify_noise = True

print('creating BAG project')
prj = bag.BagProject()

# transient test
if verify_tran==True:
    # transient test
    print('creating testbench %s__%s' % (impl_lib, tb_cell))
    tb = prj.create_testbench(tb_lib, tb_cell, impl_lib, cell_name, impl_lib)
    tb.set_parameter('cload', cload)
    tb.set_parameter('vamp', vamp_tran)

    tb.set_simulation_environments(['tt'])

    if extracted:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')

    tb.update_testbench()

    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)

    print('tckq:'+str(results['tckq']))
    print('q_samp_fF:'+str(results['q_samp_fF']))

# transient noise test
if verify_noise==True:
    print('creating testbench %s__%s' % (impl_lib, tb_noise_cell))
    tb_noise = prj.create_testbench(tb_lib, tb_noise_cell, impl_lib, cell_name, impl_lib)
    tb_noise.set_parameter('cload', cload)
    tb_noise.set_parameter('vamp', vamp_noise)

    tb_noise.set_simulation_environments(['tt'])

    if extracted:
        tb_noise.set_simulation_view(impl_lib, cell_name, 'calibre')

    tb_noise.update_testbench()

    print('running simulation')
    tb_noise.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb_noise.save_dir)
    print('0/1 ratio (0.841 for 1sigma):'+str(results['zero_one_ratio']))
