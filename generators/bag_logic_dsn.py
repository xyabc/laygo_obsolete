# -*- coding: utf-8 -*-
"""logic template generation script"""
import pprint

import bag

lib_name = 'logic_templates'
impl_lib = 'tsmcN16_logic_templates'
params = dict(lch=16e-9, pw=4, nw=4, device_intent='fast', m=1)

cell_name_dict={'tie':[2],
                'inv':[1,2,4,8],
                'tgate':[2,4,8],
                'tinv':[1,2,4,8],
                'tinv_small':[1],
                'nand':[1,2,4,8],
                'latch':[2,4,8],
                'oai22':[1],
                'mux2to1':[1,2,4,8],
                'ndsr':[1, 2],
               }


print('creating BAG project')
prj = bag.BagProject()

# create design module and run design method.
for cell_name_prim, m_list in cell_name_dict.iteritems():
    for m in m_list:
        cell_name=cell_name_prim+'_'+str(m)+'x'
        print('logic primitive:'+cell_name)
        dsn = prj.create_design_module(lib_name, cell_name_prim)
        params['m']=m
        print('design parameters:\n%s' % pprint.pformat(params))
        dsn.design(**params)
    
        # implement the design
        print('implementing design with library %s' % impl_lib)
        dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)





