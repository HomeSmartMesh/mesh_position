import utils as utl
from mqtt import mqtt_start
import json
from time import sleep

config = utl.configure_log(__file__)
graph_topic = config["graph_topic"]
print("test_graph>starting")

clientMQTT = mqtt_start(config,None,True)
print(f"test_graph>after mqtt_start")

fileName = "./test_db/graph_result_pos.json"
graph_data = utl.load_json(fileName)

sleep(1)
print(f"test_graph>after sleep")

topic = graph_topic+"/reload"
clientMQTT.publish(topic,json.dumps(graph_data))

print(f"test_graph>published {fileName} on '{topic}'")

sleep(2)
fileName = "./test_db/graph_update_pos.json"
graph_update = utl.load_json(fileName)
topic = graph_topic+"/update"
y_start = graph_update["vertices"][0]["viewBox"]["y"]
for i in range(1,10):
    graph_update["vertices"][0]["viewBox"]["y"] = y_start - i*20
    clientMQTT.publish(topic,json.dumps(graph_update))
    sleep(0.2)
print(f"test_graph>published {fileName} on '{topic}'")
