#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 17:07:45 2024

@author: yogehs
"""

# File containing the loadPARKcurve function,

import numpy as np
import pspylib.tiff.reader as tiffReader

from ..utils.forcecurve import ForceCurve
from ..utils.segment import Segment

 

def loadPARKcurve(file_metadata,curve_index = 0):
    """
    Function used to load the data of a single force curve from a PARK file.

            Parameters:
                    file_metadata (dict): Dictionary containing the file metadata.

                    curve_index (int): Index of curve to load.
            
            Returns:
                    force_curve (utils.forcecurve.ForceCurve): ForceCurve object containing the loaded data.
    """
    file_id = file_metadata['Entry_filename']
    curve_properties = file_metadata['curve_properties']
    height_channel_key = file_metadata['height_channel_key']

    
    height_curve_key = 3*curve_index
    deflection_curve_key = 3*(curve_index+1)-1
    
    park_sys_file = tiffReader.TiffReader()
    # load the Data
    park_sys_file.load(file_metadata['file_path']) 
    park_sys_FC = park_sys_file.data.spectData.rawData

    
    force_curve = ForceCurve(curve_index, file_id)

    curve_indices = file_metadata["Entry_tot_nb_curve"] 
    num_segment = file_metadata['num_segments']
    
    index = 1 if curve_indices == 0 else 3
    
 
    deflection = park_sys_FC[curve_index][int(deflection_curve_key)]
    height = park_sys_FC[curve_index][int(height_curve_key)]
    
    deflection = deflection*file_metadata[f"chanel_info_{2}"]['gain'][0]
    height = height *file_metadata[f"chanel_info_{0}"]['gain'][0]* 10**-6

    N_mid = int(len(height)/2)
    
    
    seg_pos_array =[(0,N_mid),(N_mid,len(height))]
    seg_type_arr = ['App','Ret']
    seg_dur_key = ['ramp_duration_forward','ramp_duration_reverse']
    seg_vel_key = ['speed_forward_nmbys','speed_reverse_nmbys']

        

    for segment_id in range(num_segment):
        start_pos,end_pos = seg_pos_array[segment_id]
        segment_raw_data = {}
        segment_formated_data = {}
        
        segment_type = seg_type_arr[segment_id]
        segment_duration = file_metadata[seg_dur_key[segment_id]] 
        segment_num_points = N_mid

        # TO DO: Time can be exported, handle this situation.
        segment_formated_data["time"] = np.linspace(0, segment_duration, segment_num_points, endpoint=False)
        segment_formated_data[height_channel_key] = height[start_pos:end_pos]
        segment_formated_data['vDeflection'] = deflection[start_pos:end_pos]


        segment = Segment(file_id, segment_id, segment_type)
        segment.segment_formated_data = segment_formated_data
        
        segment.segment_metadata = curve_properties[curve_index]
        #to avoind the preprocess segment 
        segment.segment_metadata['baseline_measured'] = False

        #TODO what is the set point mode 
        #segment.force_setpoint_mode = JPK_SETPOINT_MODE
        
        segment.nb_point = segment_num_points
        
        segment.nb_col = len(segment_formated_data.keys())
        
        segment.force_setpoint = file_metadata['ForceLimitVolt']
        
        segment.velocity =file_metadata[seg_vel_key[segment_id]]
        
        #segment.sampling_rate = segment.segment_metadata[f"segment_{segment_id}_sampling_rate_(S/s)"]
        #segment.z_displacement = segment.segment_metadata[f"segment_{segment_id}_Z_retract_length_(V)"]
        
        
        print(segment.segment_type)
        if segment.segment_type == "App":
            force_curve.extend_segments.append((int(segment.segment_id), segment))
            print("success")
        elif segment.segment_type == "Ret":
            force_curve.retract_segments.append((int(segment.segment_id), segment))

    return force_curve