# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml
import matplotlib.pyplot as plt

lib_name = 'adc_sar_templates'
cell_name = 'capdrv_nsw_array_8b'
impl_lib = 'adc_sar_generated'
tb_lib = 'adc_sar_testbenches'
tb_cell = 'capdrv_nsw_array_8b_tb_tran'

load_from_file=True
verify_lvs = True
extracted = True
verify_tran = True
yamlfile_system_input="adc_sar_dsn_system_input.yaml"

#spec
if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict = yaml.load(stream)
    n_bit=sysdict['n_bit']
    vh=sysdict['v_in']
    vl=0
    vcm=sysdict['v_in']/2
    trf=12e-12
    vdd=sysdict['vdd']
    c0=sysdict['c_unit']*sysdict['rdx_array'][0]
    c1=sysdict['c_unit']*sysdict['rdx_array'][1]
    c2=sysdict['c_unit']*sysdict['rdx_array'][2]
    c3=sysdict['c_unit']*sysdict['rdx_array'][3]
    c4=sysdict['c_unit']*sysdict['rdx_array'][4]
    c5=sysdict['c_unit']*sysdict['rdx_array'][5]
    c6=sysdict['c_unit']*sysdict['rdx_array'][6]
    c7=sysdict['c_unit']*sysdict['rdx_array'][7]
else:
    n_bit=9
    vh=0.3
    vl=0.0
    vcm=0.15
    trf=10e-12
    vdd=0.8
    c0=0.2e-15
    c1=0.4e-15
    c2=0.8e-15
    c3=1.6e-15
    c4=3.2e-15
    c5=6.4e-15
    c6=12.8e-15
    c7=25.6e-15

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

# transfer curve test
if verify_tran==True:
    # transient test
    print('creating testbench %s__%s' % (impl_lib, tb_cell))
    tb = prj.create_testbench(tb_lib, tb_cell, impl_lib, cell_name, impl_lib)
    tb.set_parameter('pvh', vh)
    tb.set_parameter('pvl', vl)
    tb.set_parameter('pvcm', vcm)
    tb.set_parameter('ptrf', trf)
    tb.set_parameter('pvdd', vdd)
    tb.set_parameter('pc0', c0)
    tb.set_parameter('pc1', c1)
    tb.set_parameter('pc2', c2)
    tb.set_parameter('pc3', c3)
    tb.set_parameter('pc4', c4)
    tb.set_parameter('pc5', c5)
    tb.set_parameter('pc6', c6)
    tb.set_parameter('pc7', c7)

    tb.set_simulation_environments(['tt'])

    if extracted:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')

    tb.update_testbench()

    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)
    tdelay_list=[]
    for i in range(n_bit-1):
        print("tdelay"+str(i)+":"+str(results["tdelay"+str(i)]))
        tdelay_list.append(results["tdelay"+str(i)]*1e12*2.3/0.7) 
    plt.figure(1)
    plt.plot(range(n_bit-1), tdelay_list)
    plt.show(block=False)
    plt.grid()
    plt.xlabel('digit')
    plt.ylabel('90% settling time (ps)') 
