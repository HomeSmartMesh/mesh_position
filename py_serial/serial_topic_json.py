import serial
from serial import Serial
from serial.tools import list_ports
from serial.threaded import LineReader,ReaderThread
from time import sleep
import utils as utl
import logging as log
import sys,traceback
import json

config = utl.configure_log(__file__)
ser = Serial()
on_json_function = None

def friendly_topic(topic):
    if('/' not in topic):
        return topic
    base_topic = topic.split('/')[0]
    long_name =  topic.split('/')[1]
    if(long_name in config["friendlyNames"]):
        name = config["friendlyNames"][long_name]
    else:
        name = long_name
    return base_topic+'/'+name

def get_device_ser(ser):
    dev = None
    devices = list_ports.comports()
    for device in devices:
        if(device.hwid is not None):
            hwid_split = device.hwid.split("SER=")
            if(len(hwid_split) == 2):
                serial = hwid_split[1]
                if(ser == serial):
                    dev = device.device
                    log.info(f"uart> device with serial {ser} found at {dev}")
    return dev

def get_device_id(id):
    dev = None
    devices = list_ports.comports()
    for device in devices:
        if(device.vid is not None) and (device.pid is not None):
            current_id = f"{hex(device.vid)}:{hex(device.pid)}"
            if(current_id == id):
                dev = device.device
                log.info(f"uart> device {id} found at {dev}")
    return dev

def run():
    res = None
    try:
        line = ser.readline().decode("utf-8")
        if(len(line)):
            line = line.replace('\r','')
            line = line.replace('\n','')
            splint_index = line.find("{")
            if(splint_index != -1):
                topic = friendly_topic(line[0:splint_index])
                payload = line[splint_index:]
                #print(f"topic='{topic}', payload='{payload}'")
                data = json.loads(payload)
                on_json_function(topic,data)
            elif(line.startswith("uwb_cir_acc;")):
                line_parts = line.split(";")
                data_bytes_hex = line_parts[3].split(":")[1]
                hex_data = bytearray.fromhex(data_bytes_hex)
                on_json_function("uwb_cir_acc",hex_data)
    except OSError as e:
        log.error("uart> Handled OSError exception: %s",str(e))
    except UnicodeDecodeError as e:
        log.error("uart> Handled UnicodeDecodeError exception: %s",str(e))
    return res

def send(data):
    ser.write(data.encode("ascii"))
    return

def log_port_status():
    if(ser.isOpen()):
        open_text = "is Open"
    else:
        open_text = "is Closed"
    log.info(f"uart> {ser.name} : {open_text}")
    return

def serial_stop():
    log.info("closing serial port")
    ser.flush()
    ser.close()
    log_port_status()
    return

def serial_start(config,serial_on_json):
    global on_json_function
    on_json_function = serial_on_json
    global ser
    dev = None
    if("SER" in config["serial"]):
        dev = get_device_ser(config["serial"]["SER"])
        if(dev is None):
            log.error(f"device {config['serial']['SER']} not available")
            sys.exit(1)
    elif("ID" in config["serial"]):
        dev = get_device_id(config["serial"]["ID"])
        if(dev is None):
            log.error(f"device {config['serial']['ID']} not available")
            sys.exit(1)
    else:
        dev = config["serial"]["port"]
    ser = serial.Serial(dev,
                        config["serial"]["baud"],
                        timeout=0.1)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    log_port_status()
    return ser
