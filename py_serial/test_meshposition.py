import meshposition as mp

mp.start()
list_ids = mp.rf_get_active_short_ids()

#mp.test_rf_ping_rssi("Tag",5)
#mp.test_rf_ping_all_rssi()
#mp.test_rf_all_short_id()
mp.uwb_ping_diag("Green","Tester")
mp.uwb_cir("Tester")

#mp.test_uwb_ping_diag()
#mp.test_uwb_twr_single()
#mp.test_uwb_twr_list()

#mp.db_uwb_twr("tag_four_twr")
#mp.db_uwb_ping_diag("tag_four_ping",100)

#mp.db_sid_config("config")

#mp.listen()
mp.stop()
