import serial
from serial import Serial
from serial.tools import list_ports
from serial.threaded import LineReader,ReaderThread
from time import sleep
import cfg
import logging as log
import sys,traceback
import json

config = cfg.configure_log(__file__)
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

def get_device(id):
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
            if(line.find("{") != -1):
                parts = line.split("{")
                topic = friendly_topic(parts[0])
                payload = '{'+parts[1].rstrip('\n')
                data = json.loads(payload)
                on_json_function(topic,data)
    except OSError as e:
        log.error("uart> Handled OSError exception: %s",str(e))
    except UnicodeDecodeError as e:
        log.error("uart> Handled UnicodeDecodeError exception: %s",str(e))
    return res

def send(data):
    ser.write(data.encode())
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

class PrintLines(LineReader):
    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        sys.stdout.write('serial>port opened\n')
        self.write_line('ping')

    def handle_line(self, data):
        sys.stdout.write('serial>line received: {}\n'.format(repr(data)))
        line = repr(data)
        if(len(line)):
            line = line.replace(r"\r","")
            line = line.replace(r"\n","")
            if(line.find("{") != -1):
                parts = line.split("{")
                topic = friendly_topic(parts[0])
                payload = '{'+parts[1]
                print(f"decoding '{payload}'")
                data = json.loads(payload)
                on_json_function(topic,data)

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        sys.stdout.write('serial>port closed\n')

def serial_start(config,serial_on_json):
    global on_json_function
    on_json_function = serial_on_json
    global ser
    dev = None
    if("ID" in config["serial"]):
        dev = get_device(config["serial"]["ID"])
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

def star_threaded():
    with ReaderThread(ser, PrintLines) as protocol:
        #protocol.write_line('hello')
        sleep(10)
    return