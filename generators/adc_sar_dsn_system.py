# -*- coding: utf-8 -*-

import pprint

#import bag
import numpy as np
import yaml
from math import log10

yamlfile_input="adc_sar_dsn_system_input.yaml"
yamlfile_output="adc_sar_dsn_system_output.yaml"
#load spec
with open(yamlfile_input, 'r') as stream:
    specdict = yaml.load(stream)
T=specdict['T']                      #Temperature
kT=1.38e-23*T
v_in=specdict['v_in']                #input range
n_bit=specdict['n_bit']              #number of bits
fsamp=float(specdict['fsamp'])              #effective sampling rate
c_unit=specdict['c_unit']             #minimum cap size (set by process and template)
c_m=specdict['c_m']                  #multiplier of unit cap for LSB
c0=c_unit*c_m 
c_delta=specdict['c_delta']          #Max. cap mismatch ratio for c_unit
n_bit_samp_noise=specdict['n_bit_samp_noise']   #Max. sampling noise level in bits
n_bit_samp_settle=specdict['n_bit_samp_settle'] #Max. sampling settling error level in bits
n_bit_comp_noise=specdict['n_bit_comp_noise']   #Max. comparator noise level in bits
rdx_array=np.array(specdict['rdx_array'])      #capdac radix array
rdx_enob=specdict['rdx_enob']        #enob from redundancy
v_bit=v_in/2**n_bit                  #1 bit step(ideal)
c_samp=c0*np.sum(rdx_array)          #sampling cap from c_unit
t_comp=(8-1)/9/9.6e9*0.2             #comparator timing
t_logic=(8-1)/9/9.6e9*0.4            #logic timing
t_dac=(8-1)/9/9.6e9*0.5              #DAC settling timing

print("[Top level parameters]")
print("v_bit:"+str(v_bit*1e3)+"mV")
print("c_samp:"+str(c_samp*1e15)+"fF")
#sampling noise calculaton
v_samp_noise=v_bit*n_bit_samp_noise   #sampling noise
c_samp_noise=kT/v_samp_noise**2     #sampling cap from noise requirement
c_unit_noise=c_samp_noise/2**n_bit   #unit cap calculated from noise requirement
print("")
print("[[Frontend]]")
print("")
print("[Sampling noise analysis]")
print("v_samp_noise:"+str(v_samp_noise*1e3)+"mV")
print("c_samp_noise:"+str(c_samp_noise*1e15)+"fF")
if c_samp_noise>c_samp:
    print("Sampling cap has to increase to meet noise calculation. Use a larger c_unit or c_m, or relax n_bit_samp_noise")
else:
    print("Current sampling cap meets noise specification")
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
alpha=(1.0*rdx_array[-1]/rdx_array[0])**(1.0/(n_bit-2))
rdx_test=(1-alpha**n_bit)/(1-alpha)+1-2**rdx_enob-c_delta*((1-alpha**(2*n_bit))/(1-alpha**2)+1)**0.5
print("radix:"+str(alpha))
print("ENOB test:"+str(rdx_test))
if rdx_test<0:
    print("Cannot achieve the target ENOB. Change redundancy paramters")
else:
    print("Target ENOB can be achieved for given mismatch parameters")
print("")
print("[[Comparator]]")
#comparator noise calculation
print("")
print("[Comparator noise analysis]")
v_comp_noise=v_bit*n_bit_comp_noise   #comparator noise
print("v_comp_noise:"+str(v_comp_noise*1e3)+"mV")
print("Use the noise number for comparator design")
print("")
print("[Comparator/logic/DAC timing analysis]")
print("t_comp:"+str(t_comp*1e12)+"ps")
print("t_logic:"+str(t_logic*1e12)+"ps")
print("t_dac:"+str(t_dac*1e12)+"ps")

#write to file
outdict=dict()
outdict['v_bit']=v_bit
outdict['v_comp_noise']=v_comp_noise
outdict['t_comp']=t_comp
outdict['t_logic']=t_logic
outdict['t_dac']=t_dac
with open(yamlfile_output, 'w') as stream:
    yaml.dump(outdict, stream)
