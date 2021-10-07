#!/usr/bin/python
#
#
#
# :: comment alpha 0.0.3 :: - Added modbus data decoder

import struct
import serial,time
import pymodbus
import logging
import psycopg2
import time
import json, ast
import os, sys

from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.compat import iteritems

# SYSTEM SEVER INFO
SYSTEM_SERVER_NAME = "poll_server_PYModbus"
SYSTEM_SERVER_VERSION = "alpha 0.0.3"
api_username = 'server' # default api value
api_password = '0000' # default api value
api_server = 'poll_server_PYModbus' # default api value
api_command = 'False' # default api value
si_macrosphere = 'true'
api_message = {'state':'starting'}
SYSTEM_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(level=logging.DEBUG, filename=SYSTEM_SCRIPT_DIR + '/logs/log_server.log', format='%(asctime)s %(levelname)s:%(message)s')


# USAGE FUNCTIONS
def timer_ts():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S.%f")
    return current_time

def reade_configuration():
    FILE_PATH = SYSTEM_SCRIPT_DIR + '/configurations/config.json'
    with open(FILE_PATH) as json_file:
        CFG_json_object = json.load(json_file)
        CFG_json_object = ast.literal_eval(json.dumps(CFG_json_object))

        list1 = []

        if CFG_json_object['modbus_method'] != None or CFG_json_object['modbus_method'] != '':
            list1.append( CFG_json_object['modbus_method'] )
        else:
            list1.append( 'rtu' )
        if CFG_json_object['modbus_port'] != None or CFG_json_object['modbus_port'] != '':
            list1.append( CFG_json_object['modbus_port'] )
        else:
            list1.append( '/dev/ttyUSB0' )
        if CFG_json_object['modbus_baudrate'] != None or CFG_json_object['modbus_baudrate'] != '':
            list1.append( CFG_json_object['modbus_baudrate'] )
        else:
            list1.append( 9600 )
        if CFG_json_object['modbus_timeout'] != None or CFG_json_object['modbus_timeout'] != '':
            list1.append( CFG_json_object['modbus_timeout'] )
        else:
            list1.append( 3 )
        if CFG_json_object['modbus_parity'] != None or CFG_json_object['modbus_parity'] != '':
            list1.append( CFG_json_object['modbus_parity'] )
        else:
            list1.append( 'N' )
        if CFG_json_object['modbus_stopbits'] != None or CFG_json_object['modbus_stopbits'] != '':
            list1.append( CFG_json_object['modbus_stopbits'] )
        else:
            list1.append( 1 )
        if CFG_json_object['modbus_bytesize'] != None or CFG_json_object['modbus_bytesize'] != '':
            list1.append( CFG_json_object['modbus_bytesize'] )
        else:
            list1.append( 8 )

        if CFG_json_object['reuest_interval'] != None or CFG_json_object['reuest_interval'] != '':
            list1.append( CFG_json_object['reuest_interval'] )
        else:
            list1.append( 5 )

        if CFG_json_object['holding_registers_address'] != None or CFG_json_object['holding_registers_address'] != '':
            list1.append( CFG_json_object['holding_registers_address'] )
        else:
            list1.append( 1 )
        if CFG_json_object['holding_registers_count'] != None or CFG_json_object['holding_registers_count'] != '':
            list1.append( CFG_json_object['holding_registers_count'] )
        else:
            list1.append( 3 )
        if CFG_json_object['holding_registers_unit'] != None or CFG_json_object['holding_registers_unit'] != '':
            list1.append( CFG_json_object['holding_registers_unit'] )
        else:
            list1.append( 1 )

        if CFG_json_object['postgres_user'] != None or CFG_json_object['postgres_user'] != '':
            list1.append( CFG_json_object['postgres_user'] )
        else:
            list1.append( "testuser" )
        if CFG_json_object['postgres_password'] != None or CFG_json_object['postgres_password'] != '':
            list1.append( CFG_json_object['postgres_password'] )
        else:
            list1.append( "passwd_0ne" )
        if CFG_json_object['postgres_host'] != None or CFG_json_object['postgres_host'] != '':
            list1.append( CFG_json_object['postgres_host'] )
        else:
            list1.append( "127.0.0.1" )
        if CFG_json_object['postgres_port'] != None or CFG_json_object['postgres_port'] != '':
            list1.append( CFG_json_object['postgres_port'] )
        else:
            list1.append( "5432" )
        if CFG_json_object['postgres_database'] != None or CFG_json_object['postgres_database'] != '':
            list1.append( CFG_json_object['postgres_database'] )
        else:
            list1.append( "testdb" )

        if CFG_json_object['server_name'] != None or CFG_json_object['server_name'] != '':
            list1.append( CFG_json_object['server_name'] )
        else:
            list1.append( 'poll_server_PYModbus' )
        if CFG_json_object['server_password'] != None or CFG_json_object['server_password'] != '':
            list1.append( CFG_json_object['server_password'] )
        else:
            list1.append( '0000' )
        if CFG_json_object['server_login'] != None or CFG_json_object['server_login'] != '':
            list1.append( CFG_json_object['server_login'] )
        else:
            list1.append( 'server' )

    return list1

def reade_input_API():
    FILE_PATH = SYSTEM_SCRIPT_DIR + '/buffers/api_input_data_buffer.txt'
    with open(FILE_PATH) as json_file:
        json_object = json.load(json_file)
        json_object = ast.literal_eval(json.dumps(json_object))
        #
        global api_username
        global api_password
        global api_server
        global api_command
        #
        api_username = json_object["login"]
        api_password = json_object["password"]
        api_server = json_object["server"]
        api_command = json_object["command"]
    return "OK"

def write_output_API(output_data_json):
    FILE_PATH = SYSTEM_SCRIPT_DIR + '/buffers/api_output_data_buffer.txt'
    with open(FILE_PATH, 'w') as outfile:
        json.dump(output_data_json, outfile)

def validator(instance):
    rr = instance
    raw = struct.pack('>HH', rr.getRegister(0) ,rr.getRegister(1))
    value = struct.unpack('>f', raw)[0]
    return value

def configuration_update():
    global configuration
    configuration = reade_configuration()
    return ""

configuration = reade_configuration()
write_output_API(api_message)
reade_api = reade_input_API()

client = ModbusSerialClient(
    method = configuration[0],
    port = configuration[1],
    baudrate = configuration[2],
    timeout = configuration[3],
    parity = configuration[4],
    stopbits = configuration[5],
    bytesize = configuration[6]
)

logging.debug(" reading configuration: "+str(configuration))
logging.debug(" posting 1st api message:"+str(api_message))
logging.debug(" reading 1st api message: "+str(reade_api))
logging.warning(" Server "+str(SYSTEM_SERVER_NAME)+" "+str(SYSTEM_SERVER_VERSION)+" is started")

while True:

    configuration_update()
    reade_input_API()
    api_message = {'state':'waiting'}
    write_output_API(api_message)

    if ( str(configuration[18]) == str(api_username) ) and ( str(configuration[17]) == str(api_password) ) and ( str(configuration[16]) == str(api_server) ):

        while api_command == 'True':

            api_message = {'state':'running'}
            write_output_API(api_message)
            dt = timer_ts()
            reade_input_API()
            res = ''

            #----------------------------------------------------------------------------------------------- SERVER MB RTU {
            if client.connect():                           # Trying for connect to Modbus Server/Slave
                res = client.read_holding_registers(       # Reading from a holding register with the below content
                    address = configuration[8],
                    count = configuration[9],
                    unit = configuration[10]
                )

                client.close()
                #----------------------------------------------------------------------------------------------- PREPARE DATA {
                data_value = validator(res)
                data_qual = 'true'
                # data_qual = uint16_validator(res)
                data_time = timer_ts()
                #----------------------------------------------------------------------------------------------- PREPARE DATA }
                #----------------------------------------------------------------------------------------------- DB {

                try:
                    connection = psycopg2.connect(
                        user = configuration[11],
                        password = configuration[12],
                        host = configuration[13],
                        port = configuration[14],
                        database = configuration[15]
                    )

                    postgres_insert_query = """ INSERT INTO poll_server_data (TIMESTAMP, VALUE, QUAL) VALUES (%s,%s,%s)"""
                    record_to_insert = (data_time, data_value, data_qual)

                    cursor = connection.cursor()
                    cursor.execute(postgres_insert_query, record_to_insert)
                    connection.commit()
                    count = cursor.rowcount
                    if connection:
                        cursor.close()
                        connection.close()

                except (Exception, psycopg2.Error) as error:
                    logging.error(" psycopg2 error: "+str(error))

                #----------------------------------------------------------------------------------------------- DB }
            else:
                logging.error(" Cannot connect to the Modbus Server/Slave")
                logging.error(" sleep for 30s")
                time.sleep(30)

            reade_input_API()
            #----------------------------------------------------------------------------------------------- SERVER }
            time.sleep(configuration[7])

    else:
        logging.error(" WRONG password OR login")
        logging.error(" sleep for 30s")
        time.sleep(30)
    time.sleep(1)

exit()

