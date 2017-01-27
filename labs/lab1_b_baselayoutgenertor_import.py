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

"""Lab1-b: import the layout information from BAG for a gds file
    Instructions
    1. For BAG import, copy this file to BAG working directory and uncomment BAG portions
    2. For GDS import, make sure laygo is visible in the working folder and prepare the layermap file of given
       technology (usually be found in the technology lib folder)
    3. modify metal and mpin list for given technology
"""

import laygo
#import logging;logging.basicConfig(level=logging.DEBUG)

#working library name
workinglib = 'laygo_working'

#change layer settings to becompatible with your technology
metal=[['metal0', 'donotuse'],
       ['metal1', 'drawing'],
       ['metal2', 'drawing'],
       ['metal3', 'drawing'],
       ['metal4', 'drawing'],
       ['metal5', 'drawing']]
pin=[['text', 'drawing'],
     ['metal1', 'pin'],
     ['metal2', 'pin'],
     ['metal3', 'pin'],
     ['metal4', 'pin'],
     ['metal5', 'pin']]
text=['text', 'drawing']

#generation instantiation
laygen = laygo.BaseLayoutGenerator(res=0.0025) #res should be your minimum grid resolution
#library generation
laygen.add_library(workinglib)
laygen.sel_library(workinglib)

#bag import, if bag does not exist, gds import
import imp
try:
    imp.find_module('bag')
    #bag import
    print("import from BAG")
    import bag
    prj = bag.BagProject()
    laygen.import_BAG(prj, workinglib).display()
    laygen.display()
except ImportError:
    #gds import
    print("import from GDS")
    laygen.import_GDS('lab1_generated.gds', layermapfile="laygo10n.layermap")  # change layermapfile
    laygen.import_GDS('lab1_generated2.gds', layermapfile="laygo10n.layermap")
    laygen.display()
