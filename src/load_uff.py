import os
from importutils import ForceCurve, Segment
import numpy as np

def loadUFFheader(uffpath):
    header = {}
    header['file_path'] = uffpath
    header["file_size_bytes"] = os.path.getsize(uffpath)
    header["file_type"] = os.path.splitext(uffpath)[-1]
    with open(uffpath, 'r') as file:
        for line in file.readlines():
            if 'HE' in line:
                splitline = line.split(' ', 1)[-1].split(':', 1)
                field = splitline[0]
                val = splitline[-1].lstrip().strip(' \n"')
                try: val = float(val)
                except ValueError: val = val
                header[field] = val
    return header

def loadUFFcurve(header):
    uffpath = header['file_path']
    idx = int(header['Recording_curve_id'])
    filename = header['Entry_filename']
    fdc = ForceCurve(idx, filename)
    for segid in range(int(header['Recording_number_segment'])):
        segtype = header[f'Recording_segment_{segid}_type']
        segcode = header[f'Recording_segment_{segid}_code']
        ncols = int(header[f'Recording_segment_{segid}_nb_col'])
        npoints = int(header[f'Recording_segment_{segid}_nb_point'])
        segdata = np.zeros((npoints, ncols))
        segment = Segment(filename, segid, segtype)
        with open(uffpath, 'r') as file:
            i = 0
            for line in file.readlines():
                linedata = line.split()
                if linedata[0] != segcode: continue
                for j, value in enumerate(linedata[2:]): segdata[i,j] = value
                i+=1
        for colidx in range(ncols):
            colkey = header[f'Recording_segment_{segid}_col_{colidx}_title']
            if segment.segment_formated_data is None:
                segment.segment_formated_data = {colkey:segdata[:, colidx]}
            else:
                segment.segment_formated_data.update({colkey:segdata[:, colidx]})
        if segtype == 'Approach': fdc.extend_segments.append(segment)
        elif segtype == 'Retract': fdc.retract_segments.append(segment)
        elif segtype == 'Pause': fdc.pause_segments.append(segment)
        elif segtype == 'Modulation': fdc.modulation_segments.append(segment)
    return fdc

def loadUFFtxt(uffpath, UFF):
    UFF.filemetadata = loadUFFheader(uffpath)
    return UFF