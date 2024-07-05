#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 21:25:54 2024

@author: yogehs
"""

import pspylib.tiff.reader as tiffReader

import os 

from ..constants import UFF_code, UFF_version


def parsePARKheader(filepath):
    """
    Function used to load the data of a single force curve from a PARK file.

            Parameters:
                    filepath (str): Path to the PARK file.
            
            Returns:
                    header (dict): Dictionary containing the PARK file metadata.
    """
    print("parsing park header")
    park_sys_file = tiffReader.TiffReader()
    # load the Data
    park_sys_file.load(filepath) 
    # load the Spect Header
    park_sys_meta = park_sys_file.data.spectHeader.spectHeader
    chanel_info = park_sys_file.data.spectHeader.channelInfo
    point_info= park_sys_file.data.spectHeader.pointInfo
    
    header = {}
    header["file_path"] = filepath
    header["Entry_filename"] = os.path.basename(filepath)
    header["file_size_bytes"] = os.path.getsize(filepath)
    header["file_type"] = filepath.split(os.extsep)[-1]
    header['UFF_code'] = UFF_code
    header['Entry_UFF_version'] = UFF_version
    
    


    header['force_volume'] = park_sys_meta['gridUsed'][0]
    header['spring_const_Nbym'] =     park_sys_meta['ForceConstantNewtonPerMeter'][0]
    
    header['defl_sens_nmbyV'] =    1000.0/park_sys_meta['SensitivityVoltPerMicroMeter'][0]
    header['z_closed_loop'] =     park_sys_meta['useZServo'][0]
    
    header['force_setpoint'] =     park_sys_meta['ForceLimitVolt'][0]
    header['force_setpoint_V'] =     park_sys_meta['ForceLimitVolt'][0]

    for key in park_sys_meta.keys():
        header[key] = park_sys_meta[key][0]
    # Compute parameters not stored in header
    if header['force_volume'] == 1:

        header['Entry_tot_nb_curve'] =park_sys_meta['numOfPoints'][0] 


        header['gridOffsetX'] =park_sys_meta['gridOffsetX'][0] 
        header['gridOffsetY'] =park_sys_meta['gridOffsetY'][0] 
        
        header['gridSizeWidth'] =park_sys_meta['gridSizeWidth'][0] 
        header['gridSizeHeight'] =park_sys_meta['gridSizeHeight'][0] 
        
        header['gridNumOfColumn'] =park_sys_meta['gridNumOfColumn'][0] 

    else:
        header['Entry_tot_nb_curve'] = 1
        
        
    header['ramp_size_nm'] = header['ramp_size_V'] * header['zscan_sens_nmbyV']
    
    #TODO check unit
    header['speed_forward_nmbys'] = park_sys_meta['forwardSpeed'][0] 
    header['speed_reverse_nmbys'] = park_sys_meta['backwardSpeed'][0] 
    
    
    #header['zstep_approach_nm'] = header['ramp_size_nm'] / header['nb_point_approach']
    #header['zstep_retract_nm'] = header['ramp_size_nm'] / header['nb_point_retract']
    
    header['ramp_duration_forward'] = park_sys_meta['forwardPeriod'][0] 
    header['ramp_duration_reverse'] = park_sys_meta['backwardPeriod'][0] 
    
    
    #has the gain informaiton  
    
    channel_properties = {}

    for channel_id in range(len(header['numOfChannels'])):
        channel_properties[channel_id] = chanel_info[channel_id]
        
    #empty key for curve properties for a map 
    
    header['curve_properties'] = {}
    header['curve_properties'] = point_info
    return header