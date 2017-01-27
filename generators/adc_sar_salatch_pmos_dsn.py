# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
#from adc_sar_templates_layout_generator import *
from adc_sar_salatch_pmos_layout_generator import *
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
vamp_noise=2e-3

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m=8, #larger than 8, even number
    device_intent='fast',
    )
generate_layout = False
extract_layout = False
verify = True
verify_noise = False

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

# layout
if generate_layout:
    laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")
    laygen.use_phantom = False

    tech=laygen.tech
    utemplib = tech+'_microtemplates_dense'
    logictemplib = tech+'_logic_templates'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)
 
    #library generation
    workinglib = impl_lib
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
 
    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m1m2_thick = 'route_M1_M2_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m2m3_thick = 'route_M2_M3_thick'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'
 
    m_sa=params['m'] #has to be larger than 4, even number
    m_in=int(m_sa/2)
    m_clkh=m_in
    m_rstp=1
    m_buf=max(int(m_in-4), 1)
    m_rgnp=m_in-2*m_rstp-m_buf
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)

    #salatch body
    sa_origin=np.array([0, 0])
    generate_salatch_pmos(laygen, objectname_pfix='SA0',
        placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
        routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4=rg_m3m4,
        devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
        devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
        devname_nmos_dmy='nmos4_fast_dmy_nf2',
        devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
        devname_pmos_dmy='pmos4_fast_dmy_nf2',
        devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
        m_in=m_in, m_clkh=m_clkh, m_rgnn=m_rgnp, m_rstn=m_rstp, m_buf=m_buf, origin=sa_origin)
 
    laygen.sel_cell(cell_name)
    laygen.export_BAG(prj, array_delimiter=['[', ']'])
    # run lvs
    print('running lvs')
    lvs_passed, lvs_log = prj.run_lvs(impl_lib, cell_name)
    if not lvs_passed:
        raise Exception('oops lvs died.  See LVS log file %s' % lvs_log)
    print('lvs passed')

if extract_layout==True:
    # run rcx
    print('running rcx')
    rcx_passed, rcx_log = prj.run_rcx(impl_lib, cell_name)
    if not rcx_passed:
        raise Exception('oops rcx died.  See RCX log file %s' % rcx_log)
    print('rcx passed')

if verify==True:
    # transient test
    print('creating testbench %s__%s' % (impl_lib, tb_cell))
    tb = prj.create_testbench(tb_lib, tb_cell, impl_lib, cell_name, impl_lib)
    tb.set_parameter('cload', cload)
    tb.set_parameter('vamp', vamp_tran)

    tb.set_simulation_environments(['tt'])

    if generate_layout:
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
    
        if extract_layout:
            tb_noise.set_simulation_view(impl_lib, cell_name, 'calibre')
    
        tb_noise.update_testbench()

        print('running simulation')
        tb_noise.run_simulation()

        print('loading results')
        results = bag.data.load_sim_results(tb_noise.save_dir)
        print('0/1 ratio (0.841 for 1sigma):'+str(results['zero_one_ratio']))
