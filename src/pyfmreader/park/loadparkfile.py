#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 17:46:14 2024

@author: yogehs
"""

# File containing the function loadNANOSCfile, 
# used to load the metadata of NANOSCOPE files.

from .parseparkheader import parsePARKheader

def loadPARKfile(filepath, UFF):
    """
    Function used to load the metadata of a NANOSCOPE file.

            Parameters:
                    filepath (str): File path to the NANOSCOPE file.
                    UFF (uff.UFF): UFF object to load the metadata into.
            
            Returns:
                    UFF (uff.UFF): UFF object containing the loaded metadata.
    """
    UFF.filemetadata = parsePARKheader(filepath)
    UFF.filemetadata['height_channel_key'] = 'm_height'
    UFF.filemetadata['deflection_chanel_key'] = 'vDeflection'
    UFF.filemetadata['num_segments'] = 2



    UFF.isFV = bool(UFF.filemetadata['force_volume'])
    return UFF