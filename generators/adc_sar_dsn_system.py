# -*- coding: utf-8 -*-

import pprint

import bag
import numpy as np
import yaml
from math import log10

#high level spec
T=300+100                           #temperature
kT=1.38e-23*T
vin=0.3                             #input range
nbit=8                              #number of bits
fsamp=9.6e9                         #effective sampling rate
c_unit_min=0.2e-15                  #minimum cap size from matching or min device size requirements
vbit=vin/2**nbit                    #1 bit step
nbit_samp_noise=0.25                #sampling noise level in bits
nbit_samp_settle=0.25               #sampling settling error level in bits
nbit_comp_noise=0.25                #comparator noise level in bits
#nbit_comp_kickback=0.5             #comparator kickback level in bits
v_samp_noise=vbit*nbit_samp_noise   #sampling noise
v_comp_noise=vbit*nbit_comp_noise   #comparator noise
samp_settle_error=nbit_samp_settle/nbit #settling error
samp_ntau=2.3*log10(1/samp_settle_error) #ntau of sampling network
f_samp_bw=samp_ntau*fsamp/6.28      #sampling bandwidth
c_samp_noise=kT/v_samp_noise**2     #sampling cap from noise requirement
c_unit_noise=c_samp_noise/2**nbit   #unit cap from noise requirement
c_samp_min=c_unit_min*2**nbit       #sampling cap from minimum device requirement
c_samp=max(c_samp_noise, c_samp_min) #sampling cap
r_samp=1/f_samp_bw/c_samp           #sampling network switch resistance

print("ADC top level parameters")


