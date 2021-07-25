import utils as utl
import numpy as np

data_list = []

def get_diag_param(pinger,target,paramName):
    path_list = []
    for entry in data_list:
        if((entry["pinger"] == pinger) and (entry["target"] == target)):
            path_list.append(entry["diag"][paramName])
    return np.array(path_list, dtype=np.uint16)

def plot_axis_param(paramName, pinger, target,axis):
    fpAmp = get_diag_param(pinger,target,paramName)
    axis.hist(fpAmp, bins='auto')
    axis.set_title(f"{pinger}-{target} {paramName}")

def set_data_list(dlist):
    global data_list
    data_list = dlist

def get_range(initiator,responder,twr_list):
    range_list = []
    for entry in twr_list:
        if((entry["initiator"] == initiator) and (entry["responder"] == responder)):
            if("range" not in entry):
                print(entry)
            else:
                range_list.append(entry["range"])
    return np.array(range_list, dtype=np.float64)
