from os import name
import serial_topic_json as ser
from time import sleep, perf_counter
import cfg
import threading, queue
import logging as log
import sys
import json

messages = queue.Queue()
name_to_uid = {}

def serial_on_json(topic,data):
    messages.put((topic,data))
    return

def serial_loop_forever():
    while(True):
        ser.run()

def ping_rssi(long_id):
    try:
        #start = perf_counter()
        ser.send('sm/'+long_id+'{"rf_cmd":"ping"}\r\n')
        (echotopic,echodata) = messages.get(block=True, timeout=0.2)
        (topic,data) = messages.get()
        #end = perf_counter()
        messages.task_done()
        if "rf_cmd" in data:
            if(data["rf_cmd"] == "pong"):
                return data['rssi']
        return 0
    except queue.Empty:
        return 0

def test_ping_rssi(node_name):
    uid = name_to_uid[node_name]
    for i in range(5):
        rssi = ping_rssi(uid)
        if(rssi != 0):
            print(f"test_ping({i})> rssi = {rssi}")
        else:
            print(f"test_ping({i})> failed")

def init():
    global name_to_uid
    print("mp>getting config")
    config = cfg.configure_log(__file__)
    name_to_uid = {v: k for k, v in config["friendlyNames"].items()}
    print(name_to_uid)
    print("mp>starting serial")
    ser.serial_start(config,serial_on_json)
    print("mo>start serial looping")
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
        log.error("Interrupted by user Keyboard")
        sys.exit(0)
