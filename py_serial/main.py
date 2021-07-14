import serial_topic_json as ser
from time import sleep
import logging as log
import cfg
import json
import _thread

def serial_on_json(topic,data):
    log.info(f"'{topic}' =>")
    log.info(json.dumps(data,indent=4))
    return


def serial_loop_forever():
    while(True):
        ser.run()

def main_loop_forever():
    while(True):
        sleep(1)


config = cfg.configure_log(__file__)
ser.serial_start(config,serial_on_json)

_thread.start_new_thread( serial_loop_forever, () )

main_loop_forever()
