import utils as utl
import numpy as np
import matplotlib.pyplot as plt
import meshposition as mp

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

#------------------------- Graph building -------------------------

def uwb_twr_median(initiator, responder):
    result = mp.uwb_twr(initiator=initiator,responder=responder, step_ms=10,count=10,count_ms=30)
    np_range_array = get_range(initiator, responder, result)
    median = np.median(np_range_array)
    return median

def range_graph(fileName,lists_list):
    print(f"-----------------range_graph({fileName})-----------------")
    all_entries = []
    ranges = []
    for entries in lists_list:
        initiator,responders = entries
        all_entries.append(initiator)
        for responder in responders:
            all_entries.append(responder)
            range_median = uwb_twr_median(initiator,responder)
            ranges.append({"initiator":initiator, "responder":responder, "range":round(range_median,3)})
    unique_vertices = list(set(all_entries))
    id_count = 1
    vertex_ids = {}
    vertices = []
    for vertex in unique_vertices:
        vertex_ids[vertex] = id_count
        vertices.append({"id":id_count,"label":vertex,"type":"vertex"})
        id_count = id_count + 1
    edges = []
    for range in ranges:
        entry = {
                "id":id_count,
                "label":f"{range['range']} m",
                "type":"edge",
                "inV":vertex_ids[range['initiator']],
                "outV":vertex_ids[range['responder']]
            }
        edges.append(entry)
        id_count = id_count + 1
    graph = {"vertices":vertices, "edges":edges}
    newFileName = utl.save_json_timestamp(fileName,graph)
    print(f"range_graph> saved Graphson in {newFileName}")
    return
