import paho.mqtt.client as mqtt
import time
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
import os
import re
import psutil

import mqconfig_stat as mqconfig

MQ_HOST = mqconfig.mq_host
MQ_TOPIC = mqconfig.mq_topic

count = 0
def on_connect(client, userdata, flags, rc):
    print("Connect result: {}".format(mqtt.connack_string(rc)))
    client.connected_flag = True

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed with QoS: {}".format(granted_qos[0]))

def on_message(client, userdata, msg):
    global count
    count +=1
    payload_string = msg.payload.decode('utf-8')
    print("{:d} Topic: {}. Payload: {}".format(count, msg.topic, payload_string))

def pubStatusData(client, freq=10, limit=100):
    delta = 1/freq
    
    for i in range(limit*freq):
        ti = datetime.now()

        # CPU Temp
        temp = os.popen("vcgencmd measure_temp").readline()
        da = re.findall(r'\d+\.\d+', temp.rstrip())[0]

        # CPU Use (percent)
        cpu_use = str(psutil.cpu_percent())

        # Memory Use (avail,total,percent)
        memory = psutil.virtual_memory()
        # Divide from Bytes -> KB -> MB
        total = round(memory.total/1024.0/1024.0,1)
        mem_use = str(total) + ',' + str(memory.percent)

        row = "{:s},{:s},{:s},{:s}".format(ti.strftime("%Y-%m-%d %H:%M:%S.%f"), da, cpu_use, mem_use)
        
        client.publish(MQ_TOPIC,payload=row, qos=1)
        if i%freq == 0:
            print (i, row)
        time.sleep(delta)

if __name__ == "__main__":
    print ("get client")
    client = mqtt.Client("CPU_TEMP_PUB01")
    client.username_pw_set(mqconfig.mq_user, password=mqconfig.mq_password)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    print ("Try to connect {} ".format(MQ_HOST))
    client.connect(MQ_HOST, port=1883, keepalive=120)
    print ("connected {} ".format(MQ_HOST))
    client.loop_start()
    pubStatusData(client)

    print ("sleep end")
    client.loop_stop()
