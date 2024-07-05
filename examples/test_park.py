#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 12:31:46 2024

@author: yogehs
basic usage park file  loading  

"""


from pyfmreader import loadfile

import os 
import matplotlib.pyplot as plt 
#%%
root_folder = '/Users/yogehs/Downloads/Sudiksha_data_afm_23/park_system_files/'
root_folder = '/Users/yogehs/Downloads/Sudiksha_data_afm_23/park_system_files/Map/Core/'
park_file_names = [root_folder+f for f in os.listdir(root_folder) if f.endswith('.tiff')]#glob.glob('./*.jpk-force-map')
park_file_names

#%%
# 2. Load one of the test files

park_file = loadfile(park_file_names[0])

#%%
metadata = park_file.filemetadata

for key, item in metadata.items():
    print(f"{key} : {item}\n") 
    
FC = park_file.getcurve(0)

#%%plotting 
# 6. Preprocess curve with the deflection sens in the header
defl_sens = metadata['defl_sens_nmbyV'] / 1e09 # nm/V --> m/V
FC.preprocess_force_curve(defl_sens, metadata['height_channel_key'])
plt.figure(figsize=(10,5))
for segid, segment in FC.get_segments():
    plt.plot(segment.zheight, segment.vdeflection, label=f'Segment: {segid}')
plt.xlabel('zheight [m]')
plt.ylabel('vdeflection [m]')
plt.legend()
plt.show()