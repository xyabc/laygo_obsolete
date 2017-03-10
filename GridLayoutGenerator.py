#!/usr/bin/python
########################################################################################################################
#
# Copyright (c) 2014, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################################################################

"""Grid based Layout Generator"""
__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

from .BaseLayoutGenerator import *
from .TemplateDB import *
from .GridDB import *
import numpy as np 
#from BaseLayoutGenerator import BaseLayoutGenerator
#from TemplateDB import *
#from GridDB import *
import logging

#TODO: support path routing
#TODO:

class GridLayoutGenerator(BaseLayoutGenerator):
    """Grid layout generator class

    GridLayoutGenerator is handling layout objects on abstract grids
    """
    templates = None #template database
    grids = None     #grid database
    use_phantom=False #phantom cell usage
    #phantom_layer=['prBoundary', 'drawing'] #phantom cell layer
    layers = {'metal':[], 'pin':[], 'text':[], 'prbnd':[]}


    #physical resolution
    @property
    def physical_res(self): return self.res

    @physical_res.setter
    def physical_res(self, value): self.res = value

    def __init__(self, physical_res=0.005, config_file=None):
        """
        Constructor
        """
        self.templates = TemplateDB()
        self.grids = GridDB()
        if not config_file==None: #config file exists
            with open(config_file, 'r') as stream:
                techdict = yaml.load(stream)
                self.tech = techdict['tech_lib']
                self.physical_res = techdict['physical_resolution']
                physical_res=self.physical_res
                self.layers['metal'] = techdict['metal_layers']
                self.layers['pin'] = techdict['pin_layers']
                self.layers['text'] = techdict['text_layer']
                self.layers['prbnd'] = techdict['prboundary_layer']
                print(self.tech + " loaded sucessfully")

        BaseLayoutGenerator.__init__(self, res=physical_res)

    #aux functions
    def Mt(self, transform):
        """Get transform matrix"""
        if transform=='R0':
            return np.array([[1, 0], [0, 1]])
        if transform=='MX':
            return np.array([[1, 0], [0, -1]])
        if transform=='MY':
            return np.array([[-1, 0], [0, 1]])
        if transform=='MXY': #mirror to y=x line
            return np.array([[0, 1], [1, 0]])
        if transform=='R180':
            return np.array([[-1, 0], [0, -1]])

    def Md(self, direction):
        """Get direction/projection matrix"""
        if direction== 'left':
            return np.array([[1, 0], [0, 0]])
        if direction== 'right':
            return np.array([[-1, 0], [0, 0]])
        if direction== 'top':
            return np.array([[0, 0], [0, 1]])
        if direction== 'bottom':
            return np.array([[0, 0], [0, -1]])
        if direction== 'omni':
            return np.array([[1, 0], [0, 1]])
        if direction== 'x':
            return np.array([[1, 0], [0, 0]])
        if direction== 'y':
            return np.array([[0, 0], [0, 1]])

    def sort_rect_xy(self, xy):
        """sort coordinate of rect xy"""
        bx1, bx2 = sorted(xy[:, 0].tolist())  # need to be changed..
        by1, by2 = sorted(xy[:, 1].tolist())
        ll = np.array([bx1, by1])  # lower-left
        ur = np.array([bx2, by2])  # upper-right
        bnd = np.vstack([ll, ur])
        return bnd

    #placement functions
    def place(self, name, templatename, gridname, xy, template_libname=None, shape=np.array([1, 1]), spacing=None, offset=np.array([0, 0]),
              transform='R0', annotate_text=None):
        """
        place an instantiated template on grid

        Parameters
        ----------
        name : str
            instance name to be placed
        templatename : str
            template cellname (templates.plib will be used for libname)
        gridname : str
            grid name (grids.plib will be used for cellname)
        xy : np.array([int, int])
            coordinate on specified grid
        shape : np.array([int, int])
            array shape for mosaic
        spacing : np.array([float, float])
            array spacing for mosaic
        offset : np.array([float, float])
            offset in physical cooridnate
        transform : str ('R0', 'MX', 'MY', 'R180')
            transform parameter
        annotate_text : str
            text to be annotated, None if not annotated
        """
        xy = np.asarray(xy)  # convert to numpy array
        shape = np.asarray(shape)
        if not spacing==None: spacing = np.asarray(spacing)
        offset = np.asarray(offset)
        if template_libname==None:
            template_libname=self.templates.plib
        t=self.templates.get_template(templatename, template_libname)
        xy_phy=self.grids.get_phygrid_coord_xy(gridname, xy)+offset
        #array instantiation
        if not isinstance(spacing,np.ndarray): spacing=t.size
        #if spacing==None: spacing=t.size #prints FutureWarning: comparison to `None` will result in an elementwise object comparison in the future.
        inst=self.add_inst(name=name, libname=template_libname, cellname=t.name, xy=xy_phy, shape=shape,
                           spacing=spacing, transform=transform)
        if not annotate_text==None:
            self.add_text(None, text=annotate_text, xy=np.vstack((xy_phy, xy_phy+0.5*np.dot(t.size*shape,
                          self.Mt(transform).T))), layer=self.layers['prbnd'])
        if self.use_phantom == True:
            self.add_rect(None, xy=np.vstack((xy_phy, xy_phy+np.dot(t.size*shape, self.Mt(transform).T))),
                          layer=self.layers['prbnd'])
            for pinname, pin in t.pins.items(): #pin abstract
                for x in range(shape[0]):
                    for y in range(shape[1]):
                        self.add_rect(None, xy=np.vstack((xy_phy+np.dot(pin['xy'][0]+t.size*np.array([x, y]), self.Mt(transform).T),
                                                          xy_phy+np.dot(pin['xy'][1]+t.size*np.array([x, y]), self.Mt(transform).T))),
                                      layer=self.layers['prbnd'])
                        self.add_text(None, text=pinname+'/'+pin['netname'], xy=xy_phy+
                                      0.5*np.dot(np.array([self.annotate_height, self.annotate_height]), self.Mt(transform).T)+
                                      np.dot(pin['xy'][0]+t.size*np.array([x, y]), self.Mt(transform).T)
                                      , layer=self.layers['prbnd'])
            self.add_text(None, text=inst.name+"/"+t.name, xy=xy_phy+0.5*np.dot(np.array([self.annotate_height,
                          self.annotate_height]), self.Mt(transform).T), layer=self.layers['prbnd'])

        return inst

    def relplace(self, name, templatename, gridname, refinstname, direction='left', offset=np.array([0, 0]),
                template_libname=None, shape=np.array([1, 1]), spacing=None, transform='R0'):
        """
        Relational placement

        Parameters
        ----------
        name :
        templatename :
        gridname :
        refinstname :
        direction : str
            direction of placement referenced from refinstname
        offset : np.array([0, 0])
            offset in physical coordinate
        shape :
        spacing :
        transform : str ('R0', 'MX', 'MY')
            transform parameter

        Returns
        -------

        """
        shape = np.asarray(shape)
        if not spacing == None: spacing = np.asarray(spacing)
        offset = np.asarray(offset)

        #get object information
        if template_libname==None:
            template_libname=self.templates.plib
        t=self.templates.get_template(templatename, template_libname)
        ir = self.get_inst(refinstname)
        tr = self.templates.get_template(ir.cellname, libname=ir.libname)
        #get abstract grid coordinates
        ir_xy_grid = self.grids.get_absgrid_coord_xy(gridname, ir.xy)
        tr_size_grid = self.grids.get_absgrid_coord_xy(gridname, tr.size+(ir.shape-np.array([1,1]))*ir.spacing)
        t_size_grid = self.get_template_size(templatename, gridname, libname=template_libname)
        #if not isinstance(spacing,np.ndarray): spacing=t.size
        ##if spacing==None: spacing=t.size #prints FutureWarning: comparison to `None` will result in an elementwise object comparison in the future.
        t_size_grid = t_size_grid*shape
        mtr = self.Mt(ir.transform)
        mti = self.Mt(transform)
        md = self.Md(direction)
        i_xy_grid=ir_xy_grid + 0.5*(np.dot(tr_size_grid, mtr.T) + np.dot(tr_size_grid+t_size_grid, md.T)
                                    - np.dot(t_size_grid, mti.T))
        return self.place(name=name, templatename=templatename, gridname=gridname, xy=i_xy_grid+offset,
                          template_libname=template_libname, shape=shape, spacing=spacing, transform=transform)

    def via(self, name, xy, gridname, offset=np.array([0, 0]), refinstname=None, refinstindex=np.array([0, 0]),
            refpinname=None, transform='R0'):
        """
        Place via on grid

        Parameters
        ----------
        name :
        xy :
        gridname :
        offset :
        refinstname : str
            reference instance name for xy. None if referred to origin([0, 0])
        refinstindex : str
            index of refinstname if it is a mosaic instance
        refpinname : str
            reference pin of refinstname for start point. None if referred to origin of refinstname
        offset : np.array([float, float])
            offset of xy
        transform : str
            grid transform information of grid. Overwritten by transform of refinstname if specified]
        """
        #array conversion
        xy = np.asarray(xy)
        offset = np.asarray(offset)
        refinstindex = np.asarray(refinstindex)

        #get physical grid cooridnates
        if not refinstname == None:
            refinst = self.get_inst(refinstname)
            reftemplate = self.templates.get_template(refinst.cellname, libname=refinst.libname)
            #offset = offset + refinst.xy + refinst.spacing * refinstindex
            offset = offset + refinst.xy + np.dot(refinst.spacing * refinstindex, self.Mt(refinst.transform).T)
            if not refpinname == None: #if pin reference is specified
                pin_xy_phy=reftemplate.pins[refpinname]['xy']
                pin_xy_abs=self.grids.get_absgrid_coord_region(gridname, pin_xy_phy[0], pin_xy_phy[1])[0,:]
                xy=xy+pin_xy_abs
            transform=refinst.transform #overwrite transform variable
        vianame = self.grids.get_vianame(gridname, xy)
        #print(vianame,gridname,xy)
        xy_phy=np.dot(self.grids.get_phygrid_coord_xy(gridname, xy), self.Mt(transform).T)+offset
        inst=self.add_inst(name=name, libname=self.grids.plib, cellname=vianame, xy=xy_phy, transform=transform)
        if self.use_phantom==True:
            size=self.grids.get_route_width_xy(gridname, xy)
            self.add_rect(None, xy=np.vstack((xy_phy-0.5*size, xy_phy+0.5*size)),
                          layer=self.layers['prbnd'])
            self.add_text(None, text=vianame, xy=xy_phy+0.5*np.dot(np.array([self.annotate_height,
                          self.annotate_height]), self.Mt(transform).T), layer=self.layers['prbnd'])
        return inst

    #route functions
    def route(self, name, layer, xy0, xy1, gridname0, gridname1=None, direction='omni',
              refinstname0=None, refinstname1=None, refinstindex0=np.array([0, 0]), refinstindex1=np.array([0, 0]),
              refpinname0=None, refpinname1=None, offset0=np.array([0,0]), offset1=None,
              transform0='R0', transform1=None, endstyle0="truncate", endstyle1="truncate",
              addvia0=False, addvia1=False, netname=None):
        """
        Route on grid 
        
        Parameters
        ----------

        name : str
            route name. If None, automatically assigned by genid
        layer : [str, str]
            routing layer [name, purpose]
        xy0 : np.array([int, int])
            xy coordinate for start point
        xy1 : np.array([int, int])
            xy coordinate for end point
        gridname0 : str
            grid name0
        gridname1 : str
            grid name1
        direction : str
            routing direction (omni, x, y, ...) - matrix set by Md
        refinstname0 : str
            reference instance name for start point. None if referred to origin([0, 0])
        refinstname1 : str
            reference instance name for end point. Non if referred to origin([0, 0])
        refinstindex0 : str
            index of refinstname0 if it is a mosaic instance
        refinstindex1 : str
            index of refinstname1 if it is a mosaic instance
        refpinname0 : str
            reference pin of refinstname0 for start point. None if referred to origin of refinstname0
        refpinname1 : str
            reference pin of refinstname1 for start point. None if referred to origin of refinstname1
        offset0 : np.array([float, float])
            offset of xy0
        offset1 : np.array([float, float])
            offset of xy1
        transform0 : str
            grid transform information of grid0. Overwritten by transform of refinstname0 if specified
        transform1 : str
            grid transform information of grid1. Overwritten by transform of refinstname1 if specified
        endstyle0 : str (extend, truncate)
            end style of xy0 (extend the edge by width/2 if endstyle="extend")
        endstyle1 : str (extend, truncate)
            end style of xy1 (extend the edge by width/2 if endstyle="extend")
        addvia0 : bool
            True if a via is placed on xy0
        addvia1 : bool
            True if a via is placed on xy1
        netname :
        """
        #array conversion
        xy0 = np.asarray(xy0)
        xy1 = np.asarray(xy1)
        refinstindex0 = np.asarray(refinstindex0)
        refinstindex1 = np.asarray(refinstindex1)
        offset0 = np.asarray(offset0)
        if not offset1 == None: offset1 = np.asarray(offset1)


        if gridname1 == None: gridname1 = gridname0
        if not isinstance(offset1,np.ndarray): offset1 = offset0
        #if offset1 == None: offset1 = offset0 #prints FutureWarning: comparison to `None` will result in an elementwise object comparison in the future.
        if transform1 == None: transform1 = transform0
        _xy0=xy0
        _xy1=xy1
        _offset0=offset0
        _offset1=offset1
        #reading coordinate information from reference objects
        if not refinstname0 == None:
            refinst0=self.get_inst(refinstname0)
            reftemplate0=self.templates.get_template(refinst0.cellname, libname=refinst0.libname)
            _offset0=offset0+refinst0.xy+np.dot(refinst0.spacing*refinstindex0, self.Mt(refinst0.transform).T)
            if not refpinname0 == None: #if pin reference is specified
                pin_xy0_abs=self.get_template_pin_coord(reftemplate0.name, refpinname0, gridname0, libname=refinst0.libname)[0,:]
                _xy0=xy0+pin_xy0_abs
            transform0=refinst0.transform #overwrite transform variable
        if not refinstname1 == None:
            refinst1=self.get_inst(refinstname1)
            reftemplate1=self.templates.get_template(refinst1.cellname, libname=refinst1.libname)
            _offset1=offset1+refinst1.xy+np.dot(refinst1.spacing*refinstindex1, self.Mt(refinst1.transform).T)
            if not refpinname1 == None: #if pin reference is specified
                pin_xy1_abs = self.get_template_pin_coord(reftemplate1.name, refpinname1, gridname1, libname=refinst1.libname)[0, :]
                _xy1=xy1+pin_xy1_abs
            transform1=refinst1.transform #overwrite transform variable

        #get physical grid cooridnates
        xy_phy=self._route_generate_box_from_abscoord(xy0=_xy0, xy1=_xy1, gridname0=gridname0, gridname1=gridname1,
                                                      direction=direction, offset0=_offset0, offset1=_offset1,
                                                      transform0=transform0, transform1=transform1,
                                                      endstyle0=endstyle0, endstyle1=endstyle1)
        xy0_phy=xy_phy[0,:]; xy1_phy=xy_phy[1,:]

        #optional via placement
        if addvia0==True:
            self.via(None, xy0, gridname0, offset=offset0, refinstname=refinstname0, refinstindex=refinstindex0,
            refpinname=refpinname0, transform=transform0)
        if addvia1==True:
            self.via(None, xy1, gridname1, offset=offset1, refinstname=refinstname1, refinstindex=refinstindex1,
            refpinname=refpinname1, transform=transform1)
        return self.add_rect(name, np.vstack((xy0_phy, xy1_phy)), layer, netname)

    def _route_generate_box_from_abscoord(self, xy0, xy1, gridname0, gridname1=None, direction='omni',
                                          offset0=np.array([0, 0]), offset1=None, transform0='R0', transform1=None,
                                          endstyle0="truncate", endstyle1="truncate"):
        """
        Internal function for routing and pinning.

        Generate a rectangular box from 2 points on abstracted grid.
        The thickness corresponds to the width parameter of gridname0
        
        Parameters
        ----------

        name : str
            route name. If None, automatically assigned by genid
        layer : [str, str]
            routing layer [name, purpose]
        xy0 : np.array([int, int])
            xy coordinate for start point
        xy1 : np.array([int, int])
            xy coordinate for end point
        gridname0 : str
            grid name0
        gridname1 : str
            grid name1
        direction : str
            routing direction (omni, x, y, ...) - matrix set by Md
        offset0 : np.array([float, float])
            offset of xy0
        offset1 : np.array([float, float])
            offset of xy1
        transform0 : str
            grid transform information of grid0. Overwritten by transform of refinstname0 if specified
        transform1 : str
            grid transform information of grid1. Overwritten by transform of refinstname1 if specified
        endstyle0 : str (extend, truncate)
            end style of xy0 (extend the edge by width/2 if endstyle="extend")
        endstyle1 : str (extend, truncate)
            end style of xy1 (extend the edge by width/2 if endstyle="extend")
        Returns
        -------
        np.array([[x0, y0], [x1, y1]])
        """
        if gridname1 == None: gridname1 = gridname0
        if not isinstance(offset1,np.ndarray): offset1 = offset0
        #if offset1 == None: offset1 = offset0 #prints FutureWarning: comparison to `None` will result in an elementwise object comparison in the future.
        if transform1 == None: transform1 = transform0
        xy0_phy=np.dot(self.grids.get_phygrid_coord_xy(gridname0, xy0), self.Mt(transform0).T)+offset0
        xy1_phy=np.dot(self.grids.get_phygrid_coord_xy(gridname1, xy1), self.Mt(transform1).T)+offset1
        md=self.Md(direction)
        xy1_phy=np.dot(xy1_phy - xy0_phy, md.T) + xy0_phy #adjust xy1_phy to fix routing direction
        if not (xy0_phy==xy1_phy).all(): #xy0_phy and xy1_phy should not be the same
            #generating a rect object by extending in normal directions by width/2 (routing width follows grid0)
            vwidth_direction=np.dot((xy1_phy - xy0_phy)/np.linalg.norm(xy1_phy - xy0_phy), self.Mt('MXY').T)
            vwidth_norm=0.5*self.grids.get_route_width_xy(gridname0, xy0)
            vwidth=vwidth_direction*vwidth_norm
            #endstyles
            vextend=np.array([0, 0])
            if endstyle0=="extend":
                vextend_direction = (xy1_phy - xy0_phy) / np.linalg.norm(xy1_phy - xy0_phy)
                vextend_norm = 0.5 * self.grids.get_route_width_xy(gridname0, xy0)
                vextend=vextend_direction*vextend_norm
                #print(vextend, xy0_phy, xy1_phy)
            xy0_phy = xy0_phy - vwidth - vextend
            xy1_phy = xy1_phy + vwidth + vextend
        return np.vstack((xy0_phy, xy1_phy))

    #advanced route functions
    def route_vh(self, layerv, layerh, xy0, xy1, gridname):
        """vertical-horizontal-vertical route function"""
        rh0=self.route(None, layerh, xy0=np.array([xy0[0], xy1[1]]), xy1=xy1, gridname0=gridname)
        rv0=self.route(None, layerv, xy0=np.array([xy0[0], xy1[1]]), xy1=xy0, gridname0=gridname)
        self.via(None, np.array([xy0[0], xy1[1]]), gridname=gridname)
        return [rv0, rh0]

    def route_hv(self, layerh, layerv, xy0, xy1, gridname):
        """vertical-horizontal-vertical route function"""
        rh0=self.route(None, layerh, xy0=xy0 , xy1=np.array([xy1[0], xy0[1]]), gridname0=gridname)
        rv0=self.route(None, layerv, xy0=np.array([xy1[0], xy0[1]]), xy1=xy1, gridname0=gridname)
        self.via(None, np.array([xy1[0], xy0[1]]), gridname=gridname)
        return [rh0, rv0]

    def route_vhv(self, layerv0, layerh, xy0, xy1, track_y, gridname, layerv1=None, gridname1=None, extendl=0, extendr=0):
        """vertical-horizontal-vertical route function"""
        if layerv1==None:
            layerv1=layerv0
        if gridname1==None:
            gridname1=gridname
        if xy0[0]<xy1[0]: #extend horizontal route
            xy0_0 = xy0[0] - extendl
            xy1_0 = xy1[0] + extendr
        else:
            xy0_0 = xy0[0] + extendr
            xy1_0 = xy1[0] - extendl

        #resolve grid mismatch and do horizontal route
        xy1_grid0=self.grids.get_phygrid_coord_xy(gridname, xy1)[0]
        xy1_grid1=self.grids.get_phygrid_coord_xy(gridname1, xy1)[0]
        if not xy1_grid0[0]==xy1_grid1[0]: #xy1[0] mismatch
            rh0=self.route(None, layerh, xy0=np.array([xy0_0, track_y]), xy1=np.array([xy1_0, track_y]), gridname0=gridname, offset1=np.array([xy1_grid1[0]-xy1_grid0[0], 0]))
        else:
            rh0=self.route(None, layerh, xy0=np.array([xy0_0, track_y]), xy1=np.array([xy1_0, track_y]), gridname0=gridname)
        rv0=None;rv1=None
        if not track_y == xy0[1]:
            rv0=self.route(None, layerv0, xy0=np.array([xy0[0], track_y]), xy1=xy0, gridname0=gridname, addvia0=True)
        else:
            self.via(None, xy0, gridname=gridname)
        if not track_y == xy1[1]:
            rv1=self.route(None, layerv1, xy0=np.array([xy1[0], track_y]), xy1=xy1, gridname0=gridname1, addvia0=True)
        else:
            self.via(None, xy1, gridname=gridname)
        return [rv0, rh0, rv1]

    def route_hvh(self, layerh0, layerv, xy0, xy1, track_x, gridname, layerh1=None, gridname1=None):
        """horizontal-vertical-horizontal route function"""
        if layerh1==None:
            layerh1=layerh0
        if gridname1==None:
            gridname1=gridname
        rv0 = self.route(None, layerv, xy0=np.array([track_x, xy0[1]]), xy1=np.array([track_x, xy1[1]]), gridname0=gridname)
                         #addvia0=True, addvia1=True)
        rh0=None;rh1=None
        if not track_x == xy0[0]:
            rh0=self.route(None, layerh0, xy0=xy0, xy1=np.array([track_x, xy0[1]]), gridname0=gridname, addvia1=True)
        else:
            self.via(None, xy0, gridname=gridname)
        if not track_x == xy1[0]:
            rh1=self.route(None, layerh1, xy0=np.array([track_x, xy1[1]]), xy1=xy1, gridname0=gridname, addvia0=True)
        else:
            self.via(None, xy1, gridname=gridname)
        return [rh0, rv0, rh1]

    #annotation
    def annotate_instance(self, name, annotation):
        pass

    def annotate_route(self, name, annotation):
        pass

    #pin creation functions
    def pin(self, name, layer, xy, gridname, netname=None, base_layer=None):
        """pin generation function"""
        if netname==None: netname=name
        bx1, bx2 = sorted(xy[:,0].tolist()) #need to be changed..
        by1, by2 = sorted(xy[:,1].tolist())
        ll = np.array([bx1, by1])  # lower-left
        ur = np.array([bx2, by2])  # upper-right
        bnd=np.vstack([ll,ur])
        #xy=self.grids.get_absgrid_coord_region(gridname, bnd[0,:], bnd[1,:])
        xy_phy=self._route_generate_box_from_abscoord(xy0=xy[0,:], xy1=xy[1,:], gridname0=gridname)
        if base_layer==None: base_layer=[layer[0], 'drawing'] #this is not a good way?
        self.db.add_rect(None, xy=xy_phy, layer=base_layer)
        return self.db.add_pin(name=name, netname=netname, xy=xy_phy, layer=layer)

    def pin_from_rect(self, name, layer, rect, gridname, netname=None):
        """generate a pin from a rect object"""
        if netname == None: netname = name
        xy=rect.xy
        xy = self.grids.get_absgrid_coord_region(gridname, xy[0, :], xy[1, :])
        return self.pin(name, layer, xy, gridname, netname=netname)

    def create_boundary_pin_form_rect(self, rect, gridname, pinname, layer, size=4, direction='left', netname=None):
        """create a pin object"""
        if netname == None: netname = pinname
        xy=self.get_rect_xy(rect.name, gridname, sort=True)
        if direction=="left":
            xy[1][0] = xy[0][0] + size
        elif direction=="right":
            xy[0][0] = xy[1][0] - size
        elif direction=="bottom":
            xy[1][1] = xy[0][1] + size
        elif direction=="top":
            xy[0][1] = xy[1][1] - size

        self.pin(name=pinname, layer=layer, xy=xy, gridname=gridname, netname=netname)

    #db access function
    def get_template_size(self, name, gridname, libname=None):
        """
        get template size in abstract coordinate

        Parameters
        ----------
        name : str
            template name
        gridname : str
            grid name

        Returns
        -------
        np.array([int, int])
        """
        t = self.templates.get_template(name, libname=libname)
        return self.grids.get_absgrid_coord_xy(gridname, t.size)

    def get_inst_xy(self, name, gridname):
        """
        get xy of instance in abstract coordinate

        Parameters
        ----------
        name : str
            instance name
        gridname : str
            grid name

        Returns
        -------
        np.array([int, int])
        """
        i = self.get_inst(name)
        return self.grids.get_absgrid_coord_xy(gridname, i.xy)

    def get_rect_xy(self, name, gridname, sort=False):
        """
            get xy of rect in abstract coordinate

            Parameters
            ----------
            name : str
                rect name
            gridname : str
                grid name

            Returns
            -------
            np.array([int, int])
        """
        r = self.get_rect(name)
        xy=self.grids.get_absgrid_coord_region(gridname, r.xy[0,:], r.xy[1,:])
        if sort==True: xy=self.sort_rect_xy(xy)
        return xy
        #return self.grids.get_absgrid_coord_xy(gridname, r.xy) #not always inside

    def get_pin_xy(self, name, gridname, sort=False):
        """
            get xy of rect in abstract coordinate

            Parameters
            ----------
            name : str
                rect name
            gridname : str
                grid name

            Returns
            -------
            np.array([int, int])
        """
        r = self.get_rect(name)
        xy=self.grids.get_absgrid_coord_region(gridname, r.xy[0,:], r.xy[1,:])
        if sort==True: xy=self.sort_rect_xy(xy)
        return xy

    def get_template_pin_coord(self, name, pinname, gridname, libname=None):
        """
        get xy of an template pin in abstract coordinate

        Parameters
        ----------
        name : str
            template cellname
        pinname : str
            template pinname
        gridname : str
            grid name
        libname : str
            (optional) library name of template
        Returns
        -------
        np([int, int])
        """
        t = self.templates.get_template(name, libname=libname)
        pin_xy_phy = t.pins[pinname]['xy']
        pin_xy_abs = self.grids.get_absgrid_coord_region(gridname, pin_xy_phy[0], pin_xy_phy[1])
        #pin_xy_abs[1,:] -= np.array([1, 1]) #remove offset to locate the shape in internal area
        return pin_xy_abs

    def get_inst_pin_coord(self, name, pinname, gridname, index=np.array([0, 0]), sort=False):
        """
            get xy of an instance pin in abstract coordinate

            Parameters
            ----------
            name : str
                instance name
                if None, return all pin coordinates of all instances in dict format
            pinname : str
                template pinname
                if None, return all pin coordinates of specified instance in dict format
            gridname : str
                grid name
            index : np.array([int, int])

            Returns
            -------
            np([int, int])
        """
        if name == None:
            xy=dict()
            for i in self.get_inst():
                xy[i]=self.get_inst_pin_coord(i, pinname, gridname, index, sort)
            return xy
        else:
            i = self.get_inst(name)
            t = self.templates.get_template(i.cellname, libname=i.libname)
            if pinname==None:
                xy=dict()
                for p in t.pins:
                    xy[p]=self.get_inst_pin_coord(name, p, gridname, index, sort)
                return xy
            else:
                xy0 = i.xy + np.dot(t.size * index + t.pins[pinname]['xy'][0, :], self.Mt(i.transform).T)
                xy1 = i.xy + np.dot(t.size * index + t.pins[pinname]['xy'][1, :], self.Mt(i.transform).T)

                xy=self.grids.get_absgrid_coord_region(gridname, xy0[0], xy1[0])
                if sort == True: xy = self.sort_rect_xy(xy)
                return xy

    '''
    def has_pin(self, name, pinname):
        """
            check if the instance has a pin whose name is pinname

            Parameters
            ----------
            name : str
                instance name
            pinname : str
                template pinname

            Returns
            -------
            bool
        """
        i = self.get_inst(name)
        t = self.templates.get_template(i.cellname, libname=i.libname)
        return t.pins.has_key(pinname)
    '''

    def get_inst_bbox_phygrid(self, instname):
        """
        get the bounding box of an instance

        Parameters
        ----------
        instname : str
            instance name
        """
        i = self.get_inst(instname)
        if not i.libname in self.templates.templates.keys(): #library does not exist
            return np.array([[0, 0], [0, 0]])  
        if not i.cellname in self.templates.templates[i.libname].keys(): #cell does not exist
            return np.array([[0, 0], [0, 0]]) 
        t = self.templates.get_template(i.cellname, i.libname)
        #print(i.xy, t.size, i.transform)
        if i.transform=='R0':
            return np.vstack((i.xy, i.xy+t.size*i.shape))
        if i.transform=='MX':
            return np.vstack((i.xy+t.size*np.array([0, -1])*i.shape, i.xy+t.size*np.array([1, 0])*i.shape))
        if i.transform=='MY':
            return np.vstack((i.xy+t.size*np.array([-1, 0])*i.shape, i.xy+t.size*np.array([0, 1])*i.shape))
        if i.transform=='MXY':
            return np.vstack((i.xy+t.size*np.array([0, 1])*i.shape, i.xy+t.size*np.array([1, 0])*i.shape))
        if i.transform=='R180':
            return np.vstack((i.xy+t.size*np.array([-1, -1])*i.shape, i.xy))
        #print(i.name, i.xy, t.size, i.transform)

    def get_grid(self, gridname):
        return self.grids.get_grid(gridname)

    #template and grid related functions
    def construct_template_and_grid(self, db, libname, cellname=None, layer_boundary=['prBoundary', 'boundary'],
                           routegrid_prefix='route', placementgrid_prefix='placement', append=True):
        """Construct TemplateDB and GridDB from LayoutDB"""
        tdb=TemplateDB()
        gdb=GridDB()
        tdb.add_library(libname)
        gdb.add_library(libname)

        if cellname==None:
            cellname=db.design[libname].keys()
        elif not isinstance(cellname, list):
            cellname=[cellname] # make it to a list
        for sn in cellname:
            s = db.design[libname][sn]
            if sn.startswith(placementgrid_prefix):  # placementgrid
                for r in s['rects'].values():
                    if r.layer==layer_boundary: #boundary layer
                        bx1, bx2 = sorted(r.xy[:,0].tolist()) #need to be changed..
                        by1, by2 = sorted(r.xy[:,1].tolist())
                        ll = np.array([bx1, by1])  # lower-left
                        ur = np.array([bx2, by2])  # upper-right
                        bnd=np.vstack([ll,ur])
                gdb.add_placement_grid(name=sn, libname=libname, xy=bnd)
            elif sn.startswith(routegrid_prefix): #route grid
                xgrid=[]
                xwidth=[]
                ygrid=[]
                ywidth=[]
                for r in s['rects'].values():
                    if r.layer==layer_boundary: #boundary layer
                        bx1, bx2 = sorted(r.xy[:,0].tolist()) #need to be changed..
                        by1, by2 = sorted(r.xy[:,1].tolist())
                        ll = np.array([bx1, by1])  # lower-left
                        ur = np.array([bx2, by2])  # upper-right
                        bnd=np.vstack([ll,ur])
                    else: #route
                        if r.width>r.height: # x-direction
                            ygrid.append(r.cy)
                            ywidth.append(r.height)
                        else: # y-direction
                            xgrid.append(r.cx)
                            xwidth.append(r.width)
                xg = np.vstack((np.array(xgrid), np.array(xwidth)))
                yg = np.vstack((np.array(ygrid), np.array(ywidth)))
                xg = xg.T[xg.T[:, 0].argsort()].T  # sort
                yg = yg.T[yg.T[:, 0].argsort()].T  # sort
                xgrid=xg[0,:];ygrid=yg[0,:]
                xwidth=xg[1,:];ywidth=yg[1,:]
                #print(sn, str(np.around(xg, decimals=10).tolist()), str(np.around(yg, decimals=10).tolist()))
                gdb.add_route_grid(name=sn, libname=libname, xy=bnd, xgrid=xgrid, ygrid=ygrid, xwidth=xwidth,
                                   ywidth=ywidth, viamap=None)
                #via load
                viamap=dict()
                gdb.sel_library(libname)
                for i in s['instances'].values(): #via
                    vcoord=gdb.get_absgrid_coord_xy(sn, i.xy)
                    if not i.cellname in viamap: viamap[i.cellname]=vcoord
                    else: viamap[i.cellname]=np.vstack((viamap[i.cellname],vcoord))
                for vm_name, vm_item in viamap.items():  # via map
                    #print(vm_name, vm_item, vm_item.ndim)
                    if not (vm_item.ndim==1):
                        viamap[vm_name]=vm_item[vm_item[:, 1].argsort()]
                gdb.update_viamap(sn, viamap)

            else: #normal template
                #find the boundary
                bnd=np.array(([0.0, 0.0],[0.0, 0.0]))
                for r in s['rects'].values():
                    if r.layer==layer_boundary: #boundary layer
                        bx1, bx2 = sorted(r.xy[:,0].tolist()) #need to be changed..
                        by1, by2 = sorted(r.xy[:,1].tolist())
                        ll = np.array([bx1, by1])  # lower-left
                        ur = np.array([bx2, by2])  # upper-right
                        bnd=np.vstack([ll,ur])
                #find pins
                pindict=dict()
                for t in s['texts'].values():
                    for r in s['rects'].values():
                        if r.layer==t.layer: #boundary layer
                            bx1, bx2 = sorted(r.xy[:,0].tolist()) #need to be changed..
                            by1, by2 = sorted(r.xy[:,1].tolist())
                            ll = np.array([bx1, by1])  # lower-left
                            ur = np.array([bx2, by2])  # upper-right
                            if np.all(np.logical_and(ll <= t.xy, t.xy <= ur))==True:
                                pindict[t.text]={'netname':t.text, 'layer':r.layer, 'xy':r.xy}
                logging.debug('construct_template: name:' + sn)
                tdb.add_template(name=sn, libname=libname, xy=bnd, pins=pindict)
        if append==True:
            self.templates.merge(tdb)
            self.grids.merge(gdb)
        return tdb, gdb

    def add_template_from_cell(self):
        libname=self.db.plib
        cellname=self.db.pcell

        instlist=self.db.design[libname][cellname]['instances'].keys()
        pinlist = self.db.design[libname][cellname]['pins'].keys()

        # boundaray
        ll = np.array([0.0, 0.0])
        ur = np.array([0.0, 0.0])
        #print(self.db.design[libname][cellname]['instances'].keys())
        for instname in self.db.design[libname][cellname]['instances'].keys():
            xy=self.get_inst_bbox_phygrid(instname)
            for i in range(xy.shape[0]):
                if xy[i,:][0] < ll[0]:
                    ll[0]=xy[i,:][0]
                if xy[i,:][1] < ll[1]:
                    ll[1]=xy[i,:][1]
                if xy[i,:][0] > ur[0]:
                    ur[0]=xy[i,:][0]
                if xy[i,:][1] > ur[1]:
                    ur[1]=xy[i,:][1]
        bnd=np.vstack([ll,ur])

        #find pins
        pindict = dict()
        for pinname in self.db.design[libname][cellname]['pins'].keys():
            pin=self.get_pin(pinname)
            #print(pinname, pin.layer)
            pindict[pinname]={'netname':pin.netname, 'layer':pin.layer, 'xy':pin.xy}
        self.templates.add_template(name=cellname, libname=libname, xy=bnd, pins=pindict)

    def save_template(self, filename, libname=None):
        """
        Save templateDB to yaml file
        Parameters
        ----------
        filename : str
        """
        self.templates.export_yaml(filename=filename, libname=libname)

    def load_template(self, filename, libname=None):
        """
        Load templateDB from yaml file
        Parameters
        ----------
        filename : str
        libname :
        """
        self.templates.import_yaml(filename=filename, libname=libname)

    def save_grid(self, filename):
        """
        Save gridDB to yaml file
        Parameters
        ----------
        filename : str
        """
        self.grids.export_yaml(filename=filename)

    def load_grid(self, filename, libname=None):
        """
        Load gridDB from yaml file
        Parameters
        ----------
        filename : str
        libname :
        """
        self.grids.import_yaml(filename=filename, libname=libname)
