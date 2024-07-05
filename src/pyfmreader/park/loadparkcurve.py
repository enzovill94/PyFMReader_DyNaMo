#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 17:07:45 2024

@author: yogehs
"""

# File containing the loadPARKcurve function,

from struct import unpack
from itertools import groupby
import numpy as np
from nptdms import TdmsFile
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
    deflection_chanel_key = file_metadata['deflection_chanel_key']
    
    park_sys_file = tiffReader.TiffReader()
    # load the Data
    park_sys_file.load(file_metadata['file_path']) 
    park_sys_FC = park_sys_file.data.spectData.rawData

    
    force_curve = ForceCurve(curve_index, file_id)

    curve_indices = file_metadata["Entry_tot_nb_curve"] 
    num_segment = file_metadata['num_segments']
    
    index = 1 if curve_indices == 0 else 3
    
 
    deflection = park_sys_FC[0][deflection_chanel_key]
    height = park_sys_FC[0][height_channel_key]
    N_mid = int(len(height)/2)
    
    
    seg_pos_array =[(0,N_mid),(N_mid,len(height))]
    seg_type_arr = ['App','Ret']
    
        

    for segment_id in range(num_segment):
        start_pos,end_pos = seg_pos_array[segment_id],seg_pos_array[segment_id+1]
        segment_raw_data = {}
        segment_formated_data = {}
        
        segment_type = curve_properties[str(curve_index)][segment_id][f"segment_{segment_id}_type"]
        segment_duration = curve_properties[str(curve_index)][segment_id][f"segment_{segment_id}_duration_(ticks)"]*tick_time_s
        segment_num_points = curve_properties[str(curve_index)][segment_id][f"segment_{segment_id}_nb_points_cal"]

        # TO DO: Time can be exported, handle this situation.
        segment_formated_data["time"] = np.linspace(0, segment_duration, segment_num_points, endpoint=False)
        segment_formated_data[height_channel_key] = height[start_pos:end_pos]
        segment_formated_data['vDeflection'] = deflection[start_pos:end_pos]


        segment = Segment(file_id, segment_id, segment_type)
        segment.segment_formated_data = segment_formated_data
        
        segment.segment_metadata = curve_properties[str(curve_index)][segment_id]
        #TODO what is the set point mode 
        #segment.force_setpoint_mode = JPK_SETPOINT_MODE
        
        segment.nb_point = segment_num_points
        
        segment.nb_col = len(segment_formated_data.keys())
        
        segment.force_setpoint = segment.segment_metadata[f"segment_{segment_id}_setpoint_(V)"]
        segment.velocity = segment.segment_metadata[f"segment_{segment_id}_ramp_speed_nm/s"]
        
        segment.sampling_rate = segment.segment_metadata[f"segment_{segment_id}_sampling_rate_(S/s)"]
        segment.z_displacement = segment.segment_metadata[f"segment_{segment_id}_Z_retract_length_(V)"]
        print(segment.segment_type)
        if segment.segment_type == "App":
            force_curve.extend_segments.append((int(segment.segment_id), segment))
            print("success")
        elif segment.segment_type == "Ret":
            force_curve.retract_segments.append((int(segment.segment_id), segment))
        elif segment.segment_type == "Con":
            force_curve.pause_segments.append((int(segment.segment_id), segment))
        elif segment.segment_type == "Modulation":
            force_curve.modulation_segments.append((int(segment.segment_id), segment))

    return force_curve