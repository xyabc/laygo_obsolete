# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml
from math import log10, sin, pi
import matplotlib.pyplot as plt

#parameters
lib_name = 'adc_sar_templates'
cell_name = 'sar_9b'
impl_lib = 'adc_sar_generated'
tb_lib = 'adc_sar_testbenches'
tb_cell = 'sar_9b_tb_tran_static'
load_from_file = True
verify_lvs = False
extracted = False
verify_tran = True
verify_tran_analyze = False
yamlfile_system_input = "adc_sar_dsn_system_input.yaml"
yamlfile_system_output="adc_sar_dsn_system_output.yaml"
csvfile_tf_raw = "adc_sar_tf_raw.csv"
csvfile_tf_th = "adc_sar_tf_th.csv"
csvfile_cal = "adc_sar_calcode.csv"

#spec
if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict = yaml.load(stream)
    cell_name = 'sar_'+str(sysdict['n_bit'])+'b'
    tb_cell = 'sar_'+str(sysdict['n_bit'])+'b_tb_tran_static'
    n_bit=sysdict['n_bit']
    n_bit_cal=sysdict['n_bit_cal']       
    delay=sysdict['n_interleave']/sysdict['fsamp']
    per=sysdict['n_interleave']/sysdict['fsamp']
    skew_rst=0
    vdd=sysdict['vdd']
    v_in=sysdict['v_in']             
    vicm=sysdict['v_in']/2
    vidm=sysdict['v_in']
    vref0=0
    vref1=sysdict['v_in']/2
    vref2=sysdict['v_in']
else:
    n_bit=9
    n_bit_cal=8
    delay=1e-9
    per=1e-9
    skew_rst=0
    vdd=0.8
    v_in=0.3
    vicm=0.15
    vidm=0.3
    vref0=0
    vref1=sysdict['v_in']/2
    vref2=sysdict['v_in']

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
    tb.set_parameter('pdelay', delay)
    tb.set_parameter('pper', per)
    tb.set_parameter('pskew_rst', skew_rst)
    tb.set_parameter('pvdd', vdd)
    tb.set_parameter('pvicm', vicm)
    tb.set_parameter('pvref0', vref0)
    tb.set_parameter('pvref1', vref1)
    tb.set_parameter('pvref2', vref2)
    #tb.set_parameter('pvidm', vidm)
    #tb.set_sweep_parameter('pvidm', values=[-1*vidm+i*vidm/10 for i in range(21)])
    #tb.set_sweep_parameter('pvidm', values=[-1*vidm+i*vidm/10 for i in range(3)])
    tb.set_sweep_parameter('pvidm', values=[-1*vidm+i*vidm/(2**(n_bit+1)) for i in range(2**(n_bit+1+1))])
 
    tb.set_simulation_environments(['tt'])

    if extracted:
        #tb.set_simulation_view(impl_lib, cell_name, 'calibre')
        #capdac only
        tb.set_simulation_view(impl_lib, 'capdac_'+str(n_bit-1)+'b', 'calibre')

    tb.update_testbench()
    '''
    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)
    vin=results['pvidm']
    adcout=results['adccode']
    X=np.vstack((vin,adcout)).transpose()
    np.savetxt(csvfile_tf_raw, X, fmt=['%f', '%d'], delimiter=', ')
    '''
