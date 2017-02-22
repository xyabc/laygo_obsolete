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

"""GDSII IO class for importing/exporting layout database from/to GDS. Implemented by Eric Jan"""

#TODO: Change save function to export function to maintain our naming conventions (done by Jaeduk)
#TODO: Implement text class
#TODO: Support rotations
#TODO: integrate to laygo framework
#TODO: Implement instance class (similar to SRef in python-gdsii)
#TODO: Implement import functions (similar to load in python-gdsii)

from GDSIOHelper import *


class Library(list):
    def __init__(self, version, name, physicalUnit, logicalUnit):
        """
        initialize Library object

        Parameters
        ----------
        version : int
            GDSII file version. 5 is used for v5
        name : byte string
            Library name
        physicalUnit : float
            Physical resolution
        logicalUnit : float
            Logical resolution
        """
        list.__init__(self)
        self.version = [version]
        self.name = name
        self.units = [logicalUnit, physicalUnit]
        assert physicalUnit > 0 and logicalUnit > 0

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
        stream.write(pack_data("HEADER", self.version))
        stream.write(pack_bgn("BGNLIB"))
        stream.write(pack_data("LIBNAME", self.name))
        stream.write(pack_data("UNITS", self.units))
        for struct in self:
            struct.export(stream)
        stream.write(pack_no_data("ENDLIB"))


class Structure(list):
    def __init__(self, name):
        """
        initialize Structure object

        Parameters
        ----------
        name : basestring
            Structure name
        """
        list.__init__(self)
        self.name = name

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
        stream.write(pack_bgn("BGNSTR"))
        stream.write(pack_data("STRNAME", self.name))
        for element in self:
            element.export(stream)
        stream.write(pack_no_data("ENDSTR"))


        # class Elements:
        # stores stuff ...
        # has many subclasses of elements (to be expanded in the future)
        # def __init__(self):

        # def export(self, stream):


# class Boundary (Elements):
class Boundary:
    def __init__(self, layer, dataType, points):
        """
        initialize Boundary object

        Parameters
        ----------
        layer : int
            Layer id
        dataType : int
            Layer purpose
        points : array <- to be updated to numpy.array
            xy coordinates for Boundary object
        """
        # if len(points) < 2:
        #  	raise Exception("not enough points")
        if len(points) >= 2 and points[0] != points[len(points) - 1]:
            raise Exception("start and end points different")
        temp_xy = ()
        for point in points:
            if len(point) != 2:
                raise Exception("error for point: " + str(point))
            temp_xy += point
        # Elements.__init__(self)
        self.layer = [layer]
        self.dataType = [dataType]
        self.xy = list(temp_xy)

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
        to_write = pack_no_data("BOUNDARY")
        to_write += pack_data("LAYER", self.layer)
        to_write += pack_data("DATATYPE", self.dataType)
        to_write += pack_data("XY", self.xy)
        to_write += pack_no_data("ENDEL")
        stream.write(to_write)


# class SRef:
class Instance:
    def __init__(self, sname, xy, transform='R0'):
        """
        initialize Instance object

        Parameters
        ----------
        sname : string
            Instance name
        xy : array
            xy coordinate of Instance Object
        transform : str
            transform parameter
            'R0' : default, no transform
            'R90' : rotate by 90-degree
            'R180' : rotate by 180-degree
            'R270' : rotate by 270-degree
            'MX' : mirror across X axis
            'MY' : mirror across Y axis
        """

        self.sname = sname
        if (len(xy) != 1):
            raise Exception("too many points provided\ninstance should only be located at one point")
        self.xy = xy[0]

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
        to_write = pack_no_data("SREF")
        to_write += pack_data("SNAME", self.sname)
        to_write += pack_data("XY", self.xy)
        to_write += pack_no_data("ENDEL")
        stream.write(to_write)


# class ARef:
class InstanceArray:
    def __init__(self, sname, n_col, n_row, xy, transform='R0'):
        """
        initialize Instance Array object
        Parameters
        ----------
        sname : string
            InstanceArray name
        n_col: int
            Number of columns
        n_row : int
            Number of rows
        xy : array
            xy coordinates for InstanceArray Object
            should be organized as: [(x0, y0), (x0+n_col*sp_col, y_0), (x_0, y0+n_row*sp_row)]
        transform : str
            transform parameter
            'R0' : default, no transform
            'R90' : rotate by 90-degree
            'R180' : rotate by 180-degree
            'R270' : rotate by 270-degree
            'MX' : mirror across X axis
            'MY' : mirror across Y axis
        """
        l = len(xy)
        if l != 3:
            s = "\nxy: [(x0, y0), (x0+n_col*sp_col, y_0), (x_0, y0+n_row*sp_row)]"
            if l > 3:
                s = "too many points provided" + s
            else:
                s = "not enough points provided" + s
            raise Exception(s)
        self.sname = sname
        self.colrow = [n_col, n_row]
        self.xy = [num for pt in xy for num in pt]

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
        to_write = pack_no_data("AREF")
        to_write += pack_data("SNAME", self.sname)
        to_write += pack_data("COLROW", self.colrow)
        to_write += pack_data("XY", self.xy)
        to_write += pack_no_data("ENDEL")
        stream.write(to_write)


# test
if __name__ == '__main__':
    # Create a new library
    new_lib = Library(5, b'NEWLIB.DB', 1e-9, 0.001)

    # Create a new structure
    struc = Structure('test')
    # Add the new structure to the new library
    new_lib.append(struc)

    # Add objects
    struc.append(Boundary(45, 0, [(-100000, -100000), (-100000, 0), (0, 0), (0, -100000), (-100000, -100000)]))
    struc.append(Boundary(50, 0, [(100000, 100000), (100000, 0), (0, 0), (0, 100000), (100000, 100000)]))

    struc2 = Structure('test2')
    # Add the new structure to the new library
    new_lib.append(struc2)
    # Add an instance
    struc2.append(Instance('test', [(0, 0)]))
    # Add an array instance
    struc2.append(
        InstanceArray('test', 2, 3, [(300000, 300000), (300000 + 2 * 200000, 300000), (300000, 300000 + 3 * 300000)]))

    # Export to a GDS file
    with open('testGDS.gds', 'wb') as stream:
        new_lib.export(stream)

