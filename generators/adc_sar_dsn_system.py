# -*- coding: utf-8 -*-

import pprint

#import bag
import numpy as np
import yaml
from math import log10

#high level spec
T=300+100                           #temperature
kT=1.38e-23*T
v_in=0.3                             #input range
n_bit=9                              #number of bits
fsamp=9.6e9                         #effective sampling rate
c_unit=0.205e-15                    #minimum cap size (set by process and template)
c_m=1                               #multiplier of unit cap for LSB 
c_delta=0.2                         #Max. cap mismatch ratio for c_unit
n_bit_samp_noise=0.5                 #Max. sampling noise level in bits
n_bit_samp_settle=0.5                #Max. sampling settling error level in bits
n_bit_comp_noise=0.5                 #Max. comparator noise level in bits
#n_bit_comp_kickback=0.5             #comparator kickback level in bits
v_bit=v_in/2**n_bit                    #1 bit step
c_samp=c_unit_min*2**n_bit           #sampling cap from c_unit

print("[Top level parameters]")
print("v_bit:"+str(v_bit*1e3)+"mV")
print("c_samp:"+str(c_samp*1e15)+"fF")
#noise calculaton
v_samp_noise=v_bit*n_bit_samp_noise   #sampling noise
v_comp_noise=v_bit*n_bit_comp_noise   #comparator noise
c_samp_noise=kT/v_samp_noise**2     #sampling cap from noise requirement
c_unit_noise=c_samp_noise/2**n_bit   #unit cap calculated from noise requirement
print("[Noise analysis]")
print("v_samp_noise:"+str(v_samp_noise*1e3)+"mV")
print("v_comp_noise:"+str(v_comp_noise*1e3)+"mV")
print("c_samp_noise:"+str(c_samp_noise*1e15)+"fF")

samp_settle_error=n_bit_samp_settle/n_bit #settling error
samp_ntau=2.3*log10(1/samp_settle_error) #ntau of sampling network
f_samp_bw=samp_ntau*fsamp/6.28      #sampling bandwidth
r_samp=1/f_samp_bw/c_samp           #sampling network switch resistance



