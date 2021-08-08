import utils as utl
import analyse_utils as atl
from mqtt import mqtt_start
import json
from time import sleep





def test_graph_range():
    config = utl.configure_log(__file__)
    graph_topic = config["graph_topic"]
    print("test_graph>starting")

    clientMQTT = mqtt_start(config,None,True)
    print(f"test_graph>after mqtt_start")

    fileName = "./test_db/2021.08.08/16-09-43 graph test_square_2.json"
    graph_data = utl.load_json(fileName)
    sleep(0.5)
    topic = graph_topic+"/reload"
    clientMQTT.publish(topic,json.dumps(graph_data))
    print(f"test_graph>published {fileName} on '{topic}'")

    return

def test_graph_pos():
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
    graph_update = graph_data
    topic = graph_topic+"/update"
    y_start = graph_update["vertices"][0]["viewBox"]["y"]
    for i in range(1,10):
        graph_update["vertices"][0]["viewBox"]["y"] = y_start - i*20
        clientMQTT.publish(topic,json.dumps(graph_update))
        sleep(0.2)
    print(f"test_graph>published {fileName} on '{topic}'")
    return

def test_graphlateration():
    graph_range = utl.load_json("./test_db/2021.08.08/16-27-39 graph test_square_2.json")
    positions = utl.load_json("./test_db/positions.json")
    graph_position = atl.graphlateration(graph_range,positions)
    print(f" Graph Postion => '{json.dumps(graph_position,indent=2)}'")
    return

#test_graph_range()
#test_graph_pos()
test_graphlateration()
