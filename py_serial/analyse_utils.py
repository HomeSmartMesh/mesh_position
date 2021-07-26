import utils as utl
import numpy as np
import matplotlib.pyplot as plt

data_list = []

def get_diag_param(pinger,target,paramName):
    path_list = []
    for entry in data_list:
        if((entry["pinger"] == pinger) and (entry["target"] == target)):
            if(paramName in entry["diag"]):
                path_list.append(entry["diag"][paramName])
    return np.array(path_list, dtype=np.uint16)

def plot_axis_param(paramName, pinger, target,axis):
    fpAmp = get_diag_param(pinger,target,paramName)
    axis.hist(fpAmp, bins='auto')
    median = np.median(fpAmp)
    axis.set_title(f"{pinger}-{target} {paramName} median: {round(median,1)}")

def set_data_list(dlist):
    global data_list
    data_list = dlist

def plot_ping_list_param(list,param,diag_list):
    set_data_list(diag_list)
    index = 0
    fig, axs = plt.subplots(len(list), 1, sharex=True, sharey=True)
    for (pinger,target) in list:
        plot_axis_param(param,pinger,target,axs[index])
        index = index + 1
    fig.set_size_inches(12,5)
    return

def plot_twr_list(list, twr_list):
    index = 0
    fig, axs = plt.subplots(len(list), 1, sharex=True, sharey=True)
    for (initiator,responder) in list:
        data = get_range(initiator,responder,twr_list)
        axs[index].hist(data, bins='auto')
        median = np.median(data)
        axs[index].set_title(f"{initiator}-{responder} range median : {round(median,3)}")
        index = index + 1
    fig.set_size_inches(12,3*len(list))
    return

def get_range(initiator,responder,twr_list):
    range_list = []
    for entry in twr_list:
        if((entry["initiator"] == initiator) and (entry["responder"] == responder)):
            if("range" not in entry):
                print(entry)
            else:
                range_list.append(entry["range"])
    return np.array(range_list, dtype=np.float64)
