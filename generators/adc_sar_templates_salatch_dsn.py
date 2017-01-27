# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
#from adc_sar_layout_generator import *
import numpy as np
import yaml

lib_name = 'adc_sar_templates'
cell_name = 'salatch'
impl_lib = 'adc_sar_1'
tb_lib = 'adc_sar_testbenches'
tb_cell = 'salatch_tb_tran'
test_mode = False

params = dict(
    lch=16e-9,
    pw=4,
    nw=4,
    m=10, #larger than 10, even number
    device_intent='fast',
    )
do_layout = False

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

if do_layout:
    with open("laygo_config.yaml", 'r') as stream:
        techdict = yaml.load(stream)
        tech = techdict['tech_lib']
        metal = techdict['metal_layers']
        pin = techdict['pin_layers']
        text = techdict['text_layer']
        prbnd = techdict['prboundary_layer']
        res = techdict['physical_resolution']
        print(tech + " loaded sucessfully")
    laygen = laygo.GridLayoutGenerator(physical_res=res)
    laygen.layers['metal'] = metal
    laygen.layers['pin'] = pin
    laygen.layers['prbnd'] = prbnd
    laygen.use_phantom = False
 
    utemplib = tech+'_microtemplates_dense'
    laygen.load_template(filename=utemplib+'_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=utemplib+'_grids.yaml', libname=utemplib)
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
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'
 
    m_sa=params['m'] #has to be larger than 4, even number
    m_in=int(m_sa/2)
    m_clkh=m_in
    m_rstp=1
    m_rgnp=m_in-2*m_rstp
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)
    devname_bnd_bottom=[]
    devname_bnd_top=[]
    devname_bnd_left=[]
    devname_bnd_right=[]
 
    #boundaries
    m_tot=max(m_in, m_clkh, m_rgnp+m_rstp)+1 #at least one dummy
    m_bnd=m_tot*2*2+2 #2 for diff, 2 for nf, 2 for mos boundary
    bnd_bottom_devname = ['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright']
    bnd_bottom_shape = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])]
    bnd_top_devname = ['boundary_topleft', 'boundary_top', 'boundary_topright']
    bnd_top_shape = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])]
    bnd_left_devname=['ptap_fast_left', 'nmos4_fast_left', 'nmos4_fast_left',
                      'ptap_fast_left', 'nmos4_fast_left', 'nmos4_fast_left',
                      'ptap_fast_left', 'nmos4_fast_left', 'pmos4_fast_left', 'ntap_fast_left',
                      ]
    bnd_left_transform=['R0', 'R0', 'R0',
                        'R0', 'R0', 'R0',
                        'R0', 'R0', 'MX', 'MX'
                        ]
    bnd_right_devname=['ptap_fast_right', 'nmos4_fast_right', 'nmos4_fast_right',
                       'ptap_fast_right', 'nmos4_fast_right', 'nmos4_fast_right',
                       'ptap_fast_right', 'nmos4_fast_right', 'pmos4_fast_right', 'ntap_fast_right',
                       ]
    bnd_right_transform = ['R0', 'R0', 'R0',
                          'R0', 'R0', 'R0',
                          'R0', 'R0', 'MX', 'MX'
                          ]
    [bnd_bottom, bnd_top, bnd_left, bnd_right]=generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                                                                 devname_bottom=bnd_bottom_devname,
                                                                 shape_bottom=bnd_bottom_shape,
                                                                 devname_top=bnd_top_devname,
                                                                 shape_top=bnd_top_shape,
                                                                 devname_left=bnd_left_devname,
                                                                 transform_left=bnd_left_transform,
                                                                 devname_right=bnd_right_devname,
                                                                 transform_right=bnd_right_transform,
                                                                 origin=np.array([0, 0]))
    sa_origin = laygen.get_inst_xy(bnd_bottom[0].name, pg)+laygen.get_template_size(bnd_bottom[0].cellname, pg)
    #salatch body
    generate_salatch(laygen=laygen, objectname_pfix='SA0',
                     placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                     devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
                     devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
                     devname_nmos_dmy='nmos4_fast_dmy_nf2',
                     devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
                     devname_pmos_dmy='pmos4_fast_dmy_nf2',
                     devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
                     m_in=m_in, m_clkh=m_clkh, m_rgnp=m_rgnp, m_rstp=m_rstp, origin=sa_origin)
 
    laygen.sel_cell(cell_name)
    laygen.export_BAG(prj, array_delimiter=['[', ']'])
    # run lvs
    print('running lvs')
    lvs_passed, lvs_log = prj.run_lvs(impl_lib, cell_name)
    if not lvs_passed:
        raise Exception('oops lvs died.  See LVS log file %s' % lvs_log)
    print('lvs passed')
    
    if not test_mode:
        # run rcx
        print('running rcx')
        rcx_passed, rcx_log = prj.run_rcx(impl_lib, cell_name)
        if not rcx_passed:
            raise Exception('oops rcx died.  See RCX log file %s' % rcx_log)
        print('rcx passed')

if not test_mode:
    # setup testbench
    print('creating testbench %s__%s' % (impl_lib, tb_cell))
    tb = prj.create_testbench(tb_lib, tb_cell, impl_lib, cell_name, impl_lib)

    tb.set_simulation_environments(['tt'])

    if do_layout:
        tb.set_simulation_view(impl_lib, cell_name, 'calibre')

    tb.update_testbench()

    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)

    print('tckq:'+str(results['tckq']))
    print('q_samp:'+str(results['q_samp']))

