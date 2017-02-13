# -*- coding: utf-8 -*-

import pprint

#import bag
import numpy as np
import yaml
from math import log10

#high level spec
T=300+100                           #temperature
kT=1.38e-23*T
v_in=0.4                             #input range
n_bit=9                              #number of bits
fsamp=9.6e9                         #effective sampling rate
c_unit=0.205e-15                    #minimum cap size (set by process and template)
c_m=1                               #multiplier of unit cap for LSB
c0=c_unit*c_m 
c_delta=0.2*2.7                         #Max. cap mismatch ratio for c_unit
n_bit_samp_noise=0.5                 #Max. sampling noise level in bits
n_bit_samp_settle=0.5                #Max. sampling settling error level in bits
n_bit_comp_noise=0.5                 #Max. comparator noise level in bits
#n_bit_comp_kickback=0.5             #comparator kickback level in bits
rdx_array=np.array([1, 2, 4, 8, 16, 28, 53, 100]) #capdac radix array
rdx_enob=8                          #enob from redundancy
v_bit=v_in/2**n_bit                    #1 bit step(ideal)
#c_samp=c0*2**n_bit           #sampling cap from c_unit -radix2
c_samp=c0*np.sum(rdx_array)           #sampling cap from c_unit

print("[Top level parameters]")
print("v_bit:"+str(v_bit*1e3)+"mV")
print("c_samp:"+str(c_samp*1e15)+"fF")
#sampling noise calculaton
v_samp_noise=v_bit*n_bit_samp_noise   #sampling noise
c_samp_noise=kT/v_samp_noise**2     #sampling cap from noise requirement
c_unit_noise=c_samp_noise/2**n_bit   #unit cap calculated from noise requirement
print("")
print("[Sampling noise analysis]")
print("v_samp_noise:"+str(v_samp_noise*1e3)+"mV")
print("c_samp_noise:"+str(c_samp_noise*1e15)+"fF")
if c_samp_noise>c_samp:
    print("Sampling cap has to increase to meet noise calculation. Use a larger c_unit or c_m, or relax n_bit_samp_noise")
else:
    print("Current sampling cap meets noise specification")
#comparator noise calculation
print("")
print("[Comparator noise analysis]")
v_comp_noise=v_bit*n_bit_comp_noise   #comparator noise
print("v_comp_noise:"+str(v_comp_noise*1e3)+"mV")
print("Use the noise number for comparator design")
#sampling bandwidth calculation
print("")
print("[Sampling bandwidth analysis]")
samp_settle_error=n_bit_samp_settle/n_bit #settling error
samp_ntau=2.3*log10(1/samp_settle_error) #ntau of sampling network
f_samp_bw=samp_ntau*fsamp/6.28      #sampling bandwidth
r_samp=1/f_samp_bw/c_samp           #sampling network switch resistance
print("samp_settle_error:"+str(samp_settle_error))
print("samp_ntau:"+str(samp_ntau))
print("f_samp_bw:"+str(f_samp_bw/1e9)+"GHz")
print("Use the bandwidth parameter for sampling frontend design")
#redundancy 
print("")
print("[Redundancy analysis]")
#rdx_array_ratio=np.divide(1.0*rdx_array[1:], 1.0*rdx_array[:-1])
#alpha=np.prod(rdx_array_ratio)**(1.0/n_bit)
alpha=(1.0*rdx_array[-1]/rdx_array[0])**(1.0/n_bit)
print(alpha)
rdx_test=(1-alpha**n_bit)/(1-alpha)+1-2**rdx_enob-c_delta*((1-alpha**(2*n_bit))/(1-alpha**2)+1)**0.5
print(rdx_test)
#c_delta
#rdx_array


