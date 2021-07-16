import serial_topic_json as ser
from time import sleep, perf_counter
import cfg
import threading, queue
import logging as log
import sys
import json

class mpError(Exception):
    pass
class UwbTwrArgumentError(mpError):
    pass

messages = queue.Queue()
name_to_uid = {}
base_topic = ""

def serial_on_json(topic,data):
    messages.put((topic,data))
    return

def serial_loop_forever():
    try:
        while(True):
            ser.run()
    except KeyboardInterrupt:
        log.error("ser> Interrupted by user Keyboard")
        sys.exit(0)

def init():
    global name_to_uid
    global base_topic
    print("mp>getting config")
    config = cfg.configure_log(__file__)
    name_to_uid = {v: k for k, v in config["friendlyNames"].items()}
    print(name_to_uid)
    base_topic = config["base_topic"]
    print("mp>starting serial")
    ser.serial_start(config,serial_on_json)
    print("mo>start serial parsing")
    threading.Thread(target=serial_loop_forever, daemon=True).start()

def listen():
    try:
        while(True):
            try:
                (topic,data) = messages.get(block=True, timeout=0.1)
                log.info(f"'{topic}' =>")
                log.info(json.dumps(data,indent=4))
                messages.task_done()
                sleep(0.1)
            except queue.Empty:
                sleep(0.1)
    except KeyboardInterrupt:
        log.error("listen> Interrupted by user Keyboard")
        sys.exit(0)

#------------------------- commands -------------------------

def rf_ping_rssi(node_name):
    try:
        uid = name_to_uid[node_name]
        #start = perf_counter()
        ser.send(base_topic+'/'+uid+'{"rf_cmd":"ping"}\r\n')
        (echotopic,echodata) = messages.get(block=True, timeout=0.2)
        (topic,data) = messages.get(block=True, timeout=0.2)
        #end = perf_counter()
        messages.task_done()
        if "rf_cmd" in data:
            if(data["rf_cmd"] == "pong"):
                return data['rssi']
        return 0
    except queue.Empty:
        return 0

def test_rf_ping_rssi(node_name, nb_tests):
    for i in range(nb_tests):
        rssi = rf_ping_rssi(node_name)
        if(rssi != 0):
            print(f"test_ping({i})> rssi = {rssi}")
        else:
            print(f"test_ping({i})> failed")

def uwb_ping_diag(pinger, target, at_ms=100, count=0, count_ms=0):
    try:
        command = {"uwb_cmd":"ping","pinger":pinger,"target":target,"at_ms":at_ms}
        if(count!=0):
            command["count"]="count"
        if(count_ms!=0):
            command["count_ms"]="count_ms"
        #start = perf_counter()
        ser.send(base_topic+json.dumps(command)+'\r\n')#0.222 sec
        (echotopic,echodata) = messages.get(block=True, timeout=0.4)
        (topic,data) = messages.get(block=True, timeout=0.4)
        #end = perf_counter()
        #print(f"response duration = {end-start} s")
        messages.task_done()
        if "uwb_cmd" in data:
            if(data["uwb_cmd"] == "ping"):
                return data['diag']
        return {}
    except queue.Empty:
        return {}

def test_uwb_ping_diag():
    pinger = 0
    target = 1
    diag = uwb_ping_diag(pinger, target)
    if("stdNoise" in diag):
        print(f"test_uwb_ping> ({pinger})->({target}) stdNoise = {diag['stdNoise']}")
    else:
        print(f"test_uwb_ping> failed")

def dwt_config_get(node_name="all"):
    try:
        if(node_name == "all"):
            topic_uid = base_topic
        else:
            topic_uid = base_topic+"/"+name_to_uid[node_name]
        #start = perf_counter()
        ser.send(topic_uid+'{"uwb_cmd":"config"}\r\n')
        (echotopic,echodata) = messages.get(block=True, timeout=0.2)
        if(node_name == "all"):
            #TODO separate with a loop and timeout handling in a list
            (topic,data) = messages.get(block=True, timeout=0.2)
        else:
            (topic,data) = messages.get(block=True, timeout=0.2)
        #end = perf_counter()
        messages.task_done()
        if "uwb_cmd" in data:
            if(data["uwb_cmd"] == "config"):
                return data
        return {}
    except queue.Empty:
        return {}

def dwt_config_set(node_name, chan=5,):
    return

def uwb_twr(initiator=None, responder=None, initiators=[], responders=[], at_ms=100, step_ms=None,count=None,count_ms=None):
    if(initiator is None) and (not initiators):
        raise UwbTwrArgumentError("initiator needed")
    if(responder is None) and (not responders):
        raise UwbTwrArgumentError("responder needed")
    command = {"uwb_cmd":"twr", "at_ms":at_ms}
    if(initiator is not None):
        command["initiator"] = initiator
    if(responder is not None):
        command["responder"] = responder
    if(initiators):
        command["initiators"] = initiators
    if(responders):
        command["responders"] = responders
    if(step_ms):
        command["step_ms"] = step_ms
    if(count):
        command["count"] = count
    if(count_ms):
        command["count_ms"] = count_ms
    if((len(initiators)>1) or (len(responders)>1)):
        if(not step_ms):
            raise UwbTwrArgumentError("step_ms is needed for multi step sequences")
    if count and (count > 1):
        if(not count_ms):
            raise UwbTwrArgumentError("count_ms is needed when count > 1")
    #start = perf_counter()
    ser.send(base_topic+json.dumps(command)+'\r\n')#0.209
    (echotopic,echodata) = messages.get(block=True, timeout=0.4)
    (topic,data) = messages.get(block=True, timeout=0.4)
    #end = perf_counter()
    #print(f"response duration = {end-start} s")
    messages.task_done()
    if "uwb_cmd" in data:
        if(data["uwb_cmd"] == "twr"):
            return data['range']
    return

def test_uwb_twr():
    for i in range(10):
        initiator = 0
        responder = 1
        range_measure = uwb_twr(initiator, responder)
        print(f"mp> range-{i} ({initiator})->({responder}) = {range_measure}")
    return
