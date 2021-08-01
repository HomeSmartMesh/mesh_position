import serial_topic_json as ser
from time import sleep, perf_counter
import utils as utl
import threading, queue
import logging as log
import sys
import json
import math
class mpError(Exception):
    pass
class UwbTwrArgumentError(mpError):
    pass
class UwbNoResponse(mpError):
    pass

messages = queue.Queue()
stop_messages = queue.Queue()
name_to_uid = {}
name_to_sid = {}
sid_to_name = {}
base_topic = ""
config = {}

def serial_on_json(topic,data):
    messages.put((topic,data))
    return

def serial_loop_forever():
    try:
        while(True):
            try:
                msg = stop_messages.get(block=False)
                if(msg == "close"):
                    ser.serial_stop()
                    sys.exit(0)
            except queue.Empty:
                pass
            ser.run()
    except KeyboardInterrupt:
        log.error("ser> Interrupted by user Keyboard")
        sys.exit(0)

def start():
    global name_to_uid
    global base_topic
    global config
    config = utl.configure_log(__file__)
    name_to_uid = {v: k for k, v in config["friendlyNames"].items()}
    log.debug(f"nodes in config db : {name_to_uid}")
    base_topic = config["base_topic"]
    ser.serial_start(config,serial_on_json)
    threading.Thread(target=serial_loop_forever, daemon=True).start()
    print("mp>serial thread started")

def stop():
    stop_messages.put("close")

def clear():
    print(f"clearing {messages.qsize()} entries")
    messages.queue.clear()

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

def get_short_id(node_name):
    return name_to_sid[node_name]

def rf_short_id(node_name):
    try:
        uid = name_to_uid[node_name]
        #start = perf_counter()
        ser.send(base_topic+'/'+uid+'{"rf_cmd":"sid"}\r\n')
        messages.get(block=True, timeout=0.2)
        (topic,data) = messages.get(block=True, timeout=0.2)
        #end = perf_counter()
        if "rf_cmd" in data:
            if(data["rf_cmd"] == "sid"):
                if "sid" in data:
                    return data['sid']
        raise UwbNoResponse(f"no 'rf_cmd' in response")
    except queue.Empty:
        raise UwbNoResponse(f"no response for 'rf_cmd':'sid'")

def sys_reboot(node_name):
    uid = name_to_uid[node_name]
    ser.send(base_topic+'/'+uid+'{"sys_cmd":"reboot"}\r\n')
        
def rf_get_active_short_ids():
    global name_to_sid
    global sid_to_name
    name_to_sid = {}
    sid_to_name = {}
    node_ids = {}
    for uid,fname in config["friendlyNames"].items():
        try:
            sid = rf_short_id(fname)
            node_ids[fname]={"sid":sid, "uid":uid}
            name_to_sid[fname] = sid
            sid_to_name[sid] = fname
            print(f"({fname}) : ({sid})/({uid})")
        except UwbNoResponse:
            pass
    return node_ids

#TODO count responses not supported yet
def uwb_ping_diag_sid(pinger_sid, target_sid, at_ms=100, count=0, count_ms=0):
    try:
        command = {"uwb_cmd":"ping","pinger":pinger_sid,"target":target_sid,"at_ms":at_ms}
        if(count!=0):
            command["count"]="count"
        if(count_ms!=0):
            command["count_ms"]="count_ms"
        #start = perf_counter()
        ser.send(base_topic+json.dumps(command)+'\r\n')#0.222 sec
        messages.get(block=True, timeout=0.4)
        (topic,data) = messages.get(block=True, timeout=0.4)
        #end = perf_counter()
        #print(f"response duration = {end-start} s")
        messages.task_done()
        if "uwb_cmd" in data:
            if(data["uwb_cmd"] == "ping"):
                return data['diag']
        raise UwbNoResponse(f"no 'uwb_cmd' in response")
    except queue.Empty:
        raise UwbNoResponse(f"no response from pinger({pinger_sid}) -> target({target_sid})")

def uwb_ping_diag(pinger_name, target_name, at_ms=100, count=0, count_ms=0):
    pinger_sid = name_to_sid[pinger_name]
    target_sid = name_to_sid[target_name]
    return uwb_ping_diag_sid(pinger_sid,target_sid,at_ms, count, count_ms)

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

def dwt_config_set(node_name, chan=5):
    #TODO
    return

def uwb_twr_sid(initiator=None, responder=None, initiators=[], responders=[], at_ms=100, step_ms=None,count=None,count_ms=None):
    resp_len = 1
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
        if(initiators) and (responders):
            resp_len = len(initiators) * len(responders)
        elif(initiators):
            resp_len = len(initiators)
        elif(responders):
            resp_len = len(responders)
        if(not step_ms):
            raise UwbTwrArgumentError("step_ms is needed for multi step sequences")
    if count and (count > 1):
        resp_len = resp_len * count
        if(not count_ms):
            raise UwbTwrArgumentError("count_ms is needed when count > 1")
    #start = perf_counter()
    ser.send(base_topic+json.dumps(command)+'\r\n')#0.209
    #ser.send('sm{"uwb_cmd": "twr", "at_ms": 100, "initiator": 0, "responders": [1, 2, 3, 4], "step_ms": 10}\r\n')
    received = 0
    messages.get(block=True, timeout=0.4)
    if(resp_len == 1):#simple API, returns range as single value
        try:
            (topic,data) = messages.get(block=True, timeout=0.4)
            #end = perf_counter()
            #print(f"response duration = {end-start} s")
            if "uwb_cmd" in data:
                if(data["uwb_cmd"] == "twr"):
                    received = received + 1
                    return data['range']
        except queue.Empty:
            raise UwbNoResponse(f"No response received")
    else:#returns a list
        result = []
        try:
            for i in range(resp_len):
                (topic,data) = messages.get(block=True, timeout=0.4)
                #end = perf_counter()
                #print(f"response duration = {end-start} s")
                if "uwb_cmd" in data:
                    if(data["uwb_cmd"] == "twr"):
                        del data["uwb_cmd"]
                        received = received + 1
                        result.append(data)
        except queue.Empty:
            print(f"No or not enough responses receveid({received}) / expected({resp_len})")
        return result

def uwb_twr(initiator=None, responder=None, initiators=[], responders=[], at_ms=100, step_ms=None,count=None,count_ms=None):
    initiator_sid = None
    responder_sid = None
    initiators_sid = []
    responders_sid = []
    if(initiator is not None):
        initiator_sid = name_to_sid[initiator]
    if(responder is not None):
        responder_sid = name_to_sid[responder]
    if(initiators):
        for name in initiators:
            initiators_sid.append(name_to_sid[name])
    if(responders):
        for name in responders:
            responders_sid.append(name_to_sid[name])
    result = uwb_twr_sid(initiator_sid, responder_sid, initiators_sid, responders_sid, at_ms, step_ms,count,count_ms)
    for entry in result:
        entry["initiator"] = sid_to_name[entry["initiator"]]
        entry["responder"] = sid_to_name[entry["responder"]]
    return result

def uwb_cir(receiver_name):
    #1016 sampley => 4096 bytes = 200 * 20 + 96
    try:
        uid = name_to_uid[receiver_name]
        #start = perf_counter()
        command = {"uwb_cmd":"cir_acc"}
        ser.send(base_topic+'/'+uid+json.dumps(command)+'\r\n')
        messages.get(block=True, timeout=2)
        (topic,data) = messages.get(block=True, timeout=3)
        #end = perf_counter()
        if(topic == "uwb_cir_acc"):
            return data
        raise UwbNoResponse(f"Response not valid")
    except queue.Empty:
        raise UwbNoResponse(f"No response")

#------------------------- Tests -------------------------
def test_rf_ping_rssi(node_name, nb_tests):
    for i in range(nb_tests):
        rssi = rf_ping_rssi(node_name)
        if(rssi != 0):
            print(f"test_ping({i})> rssi = {rssi}")
        else:
            print(f"test_ping({i})> failed")

def test_rf_ping_all_rssi():
    for uid,fname in config["friendlyNames"].items():
        rssi = rf_ping_rssi(fname)
        if(rssi != 0):
            print(f"test_ping({fname})> rssi = {rssi}")
        else:
            print(f"test_ping({fname})> failed")

def test_rf_all_short_id():
    for uid,fname in config["friendlyNames"].items():
        try:
            sid = rf_short_id(fname)
            print(f"get_short_id({fname}) => ({sid})")
        except UwbNoResponse:
            print(f"get_short_id({fname})> not available")

def test_uwb_ping_diag():
    pinger = "Tag"
    target = "Tester"
    diag = uwb_ping_diag(pinger, target)
    print(f"test_uwb_ping> ({pinger})->({target}) stdNoise = {diag['stdNoise']}")

def test_uwb_twr_single():
    print("-----------------test_uwb_twr_single-----------------")
    for i in range(10):
        initiator = 0
        responder = 1
        range_measure = uwb_twr(initiator, responder)
        print(f"mp> test-{i} ({initiator})->({responder}) range = {range_measure}")
    return

def test_uwb_twr_list():
    print("-----------------test_uwb_twr_list-----------------")
    initiator = 0
    responders = [1, 2, 3, 4]
    result_list = uwb_twr(initiator=initiator, responders=responders, step_ms=10)
    for res in result_list:
        print(f"mp> seq[{res['seq']}] ({res['initiator']})->({res['responder']}) range= {res['range']}")
    return

#------------------------- Database build -------------------------
def get_list_uwb_ping_diag(ping_sequence,nb_repeat):
    result_list = []
    nb_success = 0
    for i in range(nb_repeat):
        try:
            for pinger,target in ping_sequence:
                diag = uwb_ping_diag(pinger, target)
                result_list.append({"pinger":pinger, "target":target, "diag":diag,"seq":i})
            nb_success = nb_success + 1
        except UwbNoResponse:
            print(f"db_uwb_ping_diag> Skipping sequence {i} due to missing responses")
    print(f"db_uwb_ping_diag> ({nb_success})/({nb_repeat})")
    return result_list
#------------------------- Database save -------------------------

def db_uwb_twr(fileName):
    print(f"-----------------test_uwb_twr_db({fileName})-----------------")
    initiator = 0
    responders = [1, 2, 3, 4]
    result_list = uwb_twr(initiator=initiator, responders=responders, step_ms=10, count=3, count_ms=50)
    newFileName = utl.save_json_timestamp(fileName,result_list)
    print(f"db_uwb_twr> saved results in {newFileName}")
    return

def db_uwb_ping_diag(fileName,nb_repeat):
    ping_sequence = [
                        ("Tag","FrontRight"), ("Tag","FrontLeft"), ("Tag","RearLeft"), ("Tag","Tester"),
                        ("FrontRight","Tag"), ("FrontLeft","Tag"), ("RearLeft","Tag"), ("Tester","Tag")
                    ]
    result_list = get_list_uwb_ping_diag(ping_sequence, nb_repeat)
    newFileName = utl.save_json_timestamp(fileName,result_list)
    print(f"db_uwb_ping_diag> {len(result_list)} sequences saved in {newFileName}")
    return

def db_sid_config(fileName):
    print(f"-----------------db_sid_config({fileName})-----------------")
    node_ids = rf_get_active_short_ids()
    newFileName = utl.save_json_timestamp(fileName,node_ids)
    print(f"db_uwb_twr> saved results in {newFileName}")
    return

