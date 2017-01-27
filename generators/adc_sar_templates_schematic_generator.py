# -*- coding: utf-8 -*-
"""logic template generation script"""
import pprint

import bag

lib_name = 'adc_sar_templates'
impl_lib = tech_lib+'_adc_sar_templates'
params = dict(lch=16e-9, pw=4, nw=4, device_intent='fast', m=1)

cell_name_dict={'capdrv':[2, 4],
                'salatch':[8, 12, 16, 24],
                'sarlogic':[1, 2, 4],
               }


print('creating BAG project')
prj = bag.BagProject()

# create design module and run design method.
for cell_name_prim, m_list in cell_name_dict.items():
    for m in m_list:
        cell_name=cell_name_prim+'_'+str(m)+'x'
        print('adc_sar primitive:'+cell_name)
        dsn = prj.create_design_module(lib_name, cell_name_prim)
        params['m']=m
        print('design parameters:\n%s' % pprint.pformat(params))
        dsn.design(**params)
    
        # implement the design
        print('implementing design with library %s' % impl_lib)
        dsn.implement_design(impl_lib, top_cell_name=cell_name, erase=True)





