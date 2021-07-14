import serial_topic_json as ser
from time import sleep,perf_counter
import logging as log
import cfg
import json
import threading, queue

messages = queue.Queue()

def serial_on_json(topic,data):
    messages.put((topic,data))
    return

def serial_loop_forever():
    while(True):
        ser.run()

def main_loop_forever():
    while(True):
        (topic,data) = messages.get()
        log.info(f"'{topic}' =>")
        log.info(json.dumps(data,indent=4))
        messages.task_done()
        sleep(0.1)

def test_ping(long_id,test_id):
    start = perf_counter()
    ser.send('sm/'+long_id+'{"rf_cmd":"ping"}\r\n')
    (echotopic,echodata) = messages.get()
    (topic,data) = messages.get()
    end = perf_counter()
    print(f"test_ping({test_id})> roundtrip = {end-start}")
    if "rf_cmd" in data:
        if(data["rf_cmd"] == "pong"):
            log.info(f"test_ping> success rssi = {data['rssi']}")
    messages.task_done()
    return


print("main>getting config")
config = cfg.configure_log(__file__)
print("main>starting serial")
ser.serial_start(config,serial_on_json)
print("main>start serial looping")
threading.Thread(target=serial_loop_forever, daemon=True).start()
sleep(3)
for i in range(10):
    test_ping("90A971A3D1A1B648",i)

main_loop_forever()
