import meshposition as mp

mp.init()
#mp.test_rf_ping_rssi("Tag",5)
#mp.test_uwb_ping_diag()

mp.test_uwb_twr()

mp.listen()
