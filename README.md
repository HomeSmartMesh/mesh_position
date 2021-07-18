# mesh_position
High level Analysis and Apps for Mesh Position. An Ultra Wide Band RTLS with json API
# install
```shell
pip install -r requirements
pip install jupyterlab
jupyter-lab
```

# MP todos
- Python API reliable all config update

# cli test
UWB
```shell
sm{"uwb_cmd":"config"}
sm{"uwb_cmd":"ping", "pinger":0,"target":1,"at_ms":100}
sm{"uwb_cmd":"twr","initiator":0,"responder":1,"at_ms":200}

sm{"uwb_cmd":"twr","initiator":4,"responders":[0,1,2,3],"at_ms":100,"step_ms":10,"count":3,"count_ms":50}

```

RF
```shell
sm/1CF6567337562176{"rf_cmd":"ping"}
sm/1CF6567337562176{"rf_cmd":"target_ping","target":"CBC216DC164B1DE8"}
```

# test runs
RF ping RSSI
```
-----------------test_ping-----------------
test_ping(Tag)> rssi = 73
test_ping(FrontRight)> rssi = 65
test_ping(FrontLeft)> rssi = 70
test_ping(RearRight)> rssi = 58
test_ping(RearLeft)> rssi = 70
-----------------test_uwb_twr_single-----------------
mp> test-0 (0)->(1) range = 0.980
mp> test-1 (0)->(1) range = 0.994
mp> test-2 (0)->(1) range = 0.999
mp> test-3 (0)->(1) range = 1.022
mp> test-4 (0)->(1) range = 0.985
mp> test-5 (0)->(1) range = 0.990
mp> test-6 (0)->(1) range = 0.947
mp> test-7 (0)->(1) range = 0.994
mp> test-8 (0)->(1) range = 0.957
mp> test-9 (0)->(1) range = 0.990
-----------------test_uwb_twr_list-----------------
mp> seq[0] (0)->(1) range= 1.093
mp> seq[1] (0)->(2) range= 0.962
mp> seq[2] (0)->(3) range= 1.219
mp> seq[3] (0)->(4) range= 1.177

mp> seq[0] (0)->(1) range= 1.159
mp> seq[1] (0)->(2) range= 0.962
mp> seq[2] (0)->(3) range= 1.205
mp> seq[3] (0)->(4) range= 1.159

mp> seq[0] (0)->(1) range= 1.093
mp> seq[1] (0)->(2) range= 0.943
mp> seq[2] (0)->(3) range= 1.182
mp> seq[3] (0)->(4) range= 1.163
```

