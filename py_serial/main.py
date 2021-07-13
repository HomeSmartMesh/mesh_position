import serial_topic_json as ser
from time import sleep
import logging as log
import cfg
import json


def serial_on_json(topic,data):
    log.info(f"'{topic}' =>")
    log.info(json.dumps(data,indent=4))
    return


def loop_forever():
    while(True):
        sleep(0.1)
        ser.run()
    return


config = cfg.configure_log(__file__)
ser.serial_start(config,serial_on_json)

loop_forever()
