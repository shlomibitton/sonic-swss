import time
import pytest

# Counter keys on ConfigDB
PORT_KEY                  =   "PORT"
QUEUE_KEY                 =   "QUEUE"
RIF_KEY                   =   "RIF"
BUFFER_POOL_WATERMARK_KEY =   "BUFFER_POOL_WATERMARK"
PORT_BUFFER_DROP_KEY      =   "PORT_BUFFER_DROP"
PG_WATERMARK_KEY          =   "PG_WATERMARK"

# Counter stats on FlexCountersDB
PORT_STAT                  =   "PORT_STAT_COUNTER"
QUEUE_STAT                 =   "QUEUE_STAT_COUNTER"
RIF_STAT                   =   "RIF_STAT_COUNTER"
BUFFER_POOL_WATERMARK_STAT =   "BUFFER_POOL_WATERMARK_STAT_COUNTER"
PORT_BUFFER_DROP_STAT      =   "PORT_BUFFER_DROP_STAT"
PG_WATERMARK_STAT          =   "PG_WATERMARK_STAT_COUNTER"

# Counter maps on CountersDB
PORT_MAP                  =   "COUNTERS_PORT_NAME_MAP"
QUEUE_MAP                 =   "COUNTERS_QUEUE_NAME_MAP"
RIF_MAP                   =   "COUNTERS_RIF_NAME_MAP"
BUFFER_POOL_WATERMARK_MAP =   "COUNTERS_BUFFER_POOL_NAME_MAP"
PORT_BUFFER_DROP_MAP      =   "COUNTERS_PORT_NAME_MAP"
PG_WATERMARK_MAP          =   "COUNTERS_PG_NAME_MAP"

counter_type_dict = {"port_counter":[PORT_KEY, PORT_STAT, PORT_MAP],
                     "queue_counter":[QUEUE_KEY, QUEUE_STAT, QUEUE_MAP],
                     "rif_counter":[RIF_KEY, RIF_STAT, RIF_MAP],
                     "buffer_pool_watermark_counter":[BUFFER_POOL_WATERMARK_KEY, BUFFER_POOL_WATERMARK_STAT, BUFFER_POOL_WATERMARK_MAP],
                     "port_buffer_drop_counter":[PORT_BUFFER_DROP_KEY, PORT_BUFFER_DROP_STAT, PORT_BUFFER_DROP_MAP],
                     "pg_watermark_counter":[PG_WATERMARK_KEY, PG_WATERMARK_STAT, PG_WATERMARK_MAP]}

class TestFlexCounters(object):

    def setup_dbs(self, dvs):
        self.config_db = dvs.get_config_db()
        self.flex_db = dvs.get_flex_db()
        self.counters_db = dvs.get_counters_db()

    def verify_flex_counters_populated(self, map, stat):
        counters_keys = self.counters_db.db_connection.hgetall(map)
        assert len(counters_keys) > 0, str(map) + " not created in Counters DB"

        for counter_entry in counters_keys.items():
            id_list = self.flex_db.db_connection.hgetall("FLEX_COUNTER_TABLE:" + stat + ":" + counter_entry[1]).items()
            assert len(id_list) > 0, "No ID list for counter " + str(counter_entry[0])

    def enable_flex_counter_group(self, group):
        group_stats_entry = {"FLEX_COUNTER_STATUS": "enable"}
        self.config_db.create_entry("FLEX_COUNTER_TABLE", group, group_stats_entry)
        time.sleep(2)

    @pytest.mark.parametrize("counter_type", ["port_counter",
                                      "queue_counter",
                                      "rif_counter",
                                      "buffer_pool_watermark_counter",
                                      "port_buffer_drop_counter",
                                      "pg_watermark_counter"])
    def test_flex_counters(self, dvs, counter_type):
        import pdb; pdb.set_trace()
        self.setup_dbs(dvs)
        counter_key = counter_type_dict[counter_type][0]
        counter_stat = counter_type_dict[counter_type][1]
        counter_map = counter_type_dict[counter_type][2]

        if counter_type == "rif_counter":
            self.config_db.db_connection.hset('INTERFACE|Ethernet0', "NULL", "NULL")
            self.config_db.db_connection.hset('INTERFACE|Ethernet0|192.168.0.1/24', "NULL", "NULL")

        self.enable_flex_counter_group(counter_key)
        self.verify_flex_counters_populated(counter_map, counter_stat)

        if counter_type == "rif_counter":
            self.config_db.db_connection.hdel('INTERFACE|Ethernet0|192.168.0.1/24', "NULL")

