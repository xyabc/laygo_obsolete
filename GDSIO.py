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
        stream.write(pack_int("HEADER", self.version))
        stream.write(pack_bgn("BGNLIB"))
        stream.write(pack_text("LIBNAME", self.name))
        stream.write(pack_double("UNITS", self.units))
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
        stream.write(pack_text("STRNAME", self.name))
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
        stream.write(pack_no_data("BOUNDARY"))
        stream.write(pack_int("LAYER", self.layer))
        stream.write(pack_int("DATATYPE", self.dataType))
        stream.write(pack_long("XY", self.xy))
        stream.write(pack_no_data("ENDEL"))

class Instance:
    def __init__(self):
        """
        initialize An Instance object
        """

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """

class InstanceArray:
    def __init__(self):
        """
        initialize An Instance object
        """

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
#test
if __name__ == '__main__':
    # Create a new library
    new_lib = Library(5, b'NEWLIB.DB', 1e-9, 0.001)

    # Create a new structure
    struc = Structure('test')
    # Add the new structure to the new library
    new_lib.append(struc)

    # Add objects
    struc.append(Boundary(45, 0, [(-100000, -100000), (-100000, 0), (0,0), (0, -100000), (-100000, -100000)]))
    struc.append(Boundary(50, 0, [(100000, 100000), (100000, 0), (0,0), (0, 100000), (100000, 100000)]))
    # struc.append(Boundary(57, 0, [(10000, 10000), (10000, 0), (0,0), (0, 10000), (10000, 1000000)]))
    # struc.append(Boundary(288, 0, [(1, 1), (1, 0), (0,0), (0, 1), (1, 1)]))imp

    # Exprot to a GDS file
    with open('testGDS.gds', 'wb') as stream:
        new_lib.export(stream)

