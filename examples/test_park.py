#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 12:31:46 2024

@author: yogehs
basic usage park file  loading  

"""


from pyfmreader import loadfile
from pyfmrheo import doHertzFit

import os 
import matplotlib.pyplot as plt 
#%%
root_folder = '/Users/yogehs/Downloads/Sudiksha_data_afm_23/park_system_files/'
#root_folder = '/Users/yogehs/Downloads/Sudiksha_data_afm_23/park_system_files/Map/Core/'
park_file_names = [root_folder+f for f in os.listdir(root_folder) if f.endswith('.tiff')]#glob.glob('./*.jpk-force-map')
park_file_names

#%%
# 2. Load one of the test files

park_file = loadfile(park_file_names[0])

#%%
filemetadata = park_file.filemetadata

for key, item in filemetadata.items():
    print(f"{key} : {item}\n") 
    
FC = park_file.getcurve(0)
#%%hertz fitting 
# Define parameters to perform the HertzFit

# Get some of the file metadata
closed_loop = filemetadata['z_closed_loop']
file_deflection_sensitivity = filemetadata['defl_sens_nmbyV'] #nm/V
file_spring_constant = filemetadata['spring_const_Nbym'] #N/m
height_channel = filemetadata['height_channel_key']

deflection_sensitivity = file_deflection_sensitivity / 1e9 #m/V
spring_constant = file_spring_constant

print(f"Closed loop: {closed_loop}")
print(f"Height channel: {height_channel}")
print(f"Deflection Sens.: {deflection_sensitivity} m/V")
print(f"Spring Constant: {spring_constant} N/m")
maxnoncontact = 1e-6 #um

param_dict = {
    'height_channel': height_channel,   # Channel where to find the height data
    'def_sens': deflection_sensitivity, # Deflection sensitivity in m/V
    'k': spring_constant,               # Spring constant in N/m
    'contact_model': 'pyramid',      # Geometry of the indenter: paraboloidal, conical, pyramidal
    'tip_param': 35,                 # Tip raidus in meters or tip angle in degrees
    'curve_seg': 'extend',              # Segement to perform the fit: extend or retract
    'correct_tilt': True,              # Perform tilt correction
    'tilt_min_offset': 1e-08,           # Maximum range where to perform the tilt correction in meters
    'tilt_max_offset': 1e-06,           # Minimum range where to perform the tilt correction in meters
    'poisson': 0.5,                     # Poisson's ratio
    'poc_method': 'RoV',                # Method to find the contact point: RoV or RegulaFalsi
    'poc_win': 3,                   # Window size for the RoV method
    'max_ind': 0.0,                     # Maximum indentation range for fit in meters
    'min_ind': 1000e-09,                     # Minimum indentation range for fit in meters
    'max_force': 0.0,                   # Maximum force range for fit in Newtons
    'min_force': 0.0,                   # Minimum force range for fit in Newtons
    'fit_range_type': 'full',           # Fit data range: full, indentation or force
    'd0': 0.0,                          # Initial point of contact
    'slope': 0.0,                       # Initial slope
    'auto_init_E0': True,               # Estimate automatically the initial value of the Young's Modulus
    'E0': 500,                         # Initial Young's Modulus value
    'f0': 0.0,                          # Initial F0 value
    'contact_offset': maxnoncontact,    # Baseline offset for the Hertz Fit
    'fit_line': False,                  # Fit line to the baseline
    'downsample_flag': False,            # Downsample the signal for Hertz Fit
    'pts_downsample': 0,   # Number of points to downsample
    'offset_type':'percentage',         # How to correct for baseline offset: percentage or value
    'max_offset':.3,                    # Max percentage to compute offset
    'min_offset':0.1                      # Min percentage to compute offset
}
FC.preprocess_force_curve(defl_sens, filemetadata['height_channel_key'])

hertz_result = doHertzFit(FC, param_dict)
hertz_result.fit_report()

#%%plotting 
# 6. Preprocess curve with the deflection sens in the header
defl_sens = filemetadata['defl_sens_nmbyV'] / 1e09 # nm/V --> m/V
FC.preprocess_force_curve(defl_sens, filemetadata['height_channel_key'])
file_spring_constant = filemetadata['spring_const_Nbym']  # N/m

FC.get_force_vs_indentation([0,0], file_spring_constant)
plt.figure(figsize=(10,5))
for segid, segment in FC.get_segments():
    print(segment.zheight)
    plt.plot(-1*segment.zheight, segment.force, label=f'Segment: {segid}')
plt.xlabel('zheight [m]')
plt.ylabel('vdeflection [m]')
plt.legend()
plt.show()