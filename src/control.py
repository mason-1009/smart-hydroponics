#!/usr/bin/env python3

import serial
import json

class Controller(object):
    
    # define commandID constants
    # GET_DATA=0
    # SET_GROWTH_LAMP=1
    # SET_AMBIENT_LIGHTING=2
    # SET_WATERING_CYCLE_START=3
    INFO_CMD=1
    ENABLE_GROWTH_LAMP_CMD=2
    DISABLE_GROWTH_LAMP_CMD=3
    ENABLE_AMBIENT_LAMP_CMD=4
    DISABLE_AMBIENT_LAMP_CMD=5
    ENABLE_WATERING_CYCLE_CMD=6
    DISABLE_WATERING_CYCLE_CMD=7

    # Pi-to-Arduino communication utilizes commands and data transmission via JSON
    # define arduino hardware-related objects
    serialObject=None
    serialPort=None
    serialBaud=None

    # define variable for received serial data
    received=dict()
    received["soilHumidity"]=None
    received["soilTemperature"]=None
    received["ambientLightState"]=None
    received["growthLampState"]=None
    received["wateringCycleState"]=None
    
    def genCmdPacket(self, commandID):
        # generate JSON command packet to be sent over serial
        unicodeString=json.dumps({"command":commandID})
        # add CRLF characters for serial communication
        return unicodeString.encode("utf-8")+serial.CR+serial.LF

    def initiallizeSerial(self):
        # create serial object
        self.serialObject=serial.Serial(port=self.serialPort,baudrate=self.serialBaud)

    def __init__(self, serialPort="/dev/ttyACM0", serialBaud=9600):
        # set class data and init objects
        self.serialPort=serialPort
        self.serialBaud=serialBaud
        self.initiallizeSerial()

    def parseResponse(self):
        try:
            returnData=json.loads(self.serialObject.readline().decode("utf-8"))
            self.received["soilHumidity"]=returnData.get("gmHumidity")
            self.received["soilTemperature"]=returnData.get("temperature")
            self.received["growthLampState"]=returnData.get("growthLampStatus")
            self.received["ambientLightState"]=returnData.get("ambientLightingStatus")
            self.received["wateringCycleState"]=returnData.get("wateringCycleStatus")
            return True
        except json.decoder.JSONDecodeError:
            return False

    def fetchInformation(self):
        # send GET_DATA command
        try:
            self.serialObject.write(self.genCmdPacket(self.INFO_CMD))
        except serial.serialutil.SerialException:
            return False
        # immediately listen for response line (WARNING: blocking) and assign values
        return self.parseResponse()

    def setGrowthLamp(self, state):
        # send command
        try:
            self.serialObject.write(self.genCmdPacket((self.DISABLE_GROWTH_LAMP_CMD,self.ENABLE_GROWTH_LAMP_CMD)[state]))
        except serial.serialutil.SerialException:
            return False
        return True

    def setAmbientLight(self, state):
        # send command
        try:
            self.serialObject.write(self.genCmdPacket((self.DISABLE_AMBIENT_LIGHTING_CMD,self.ENABLE_AMBIENT_LIGHTING_CMD)[state]))
        except serial.serialutil.SerialException:
            return False
        return True

    def setWateringCycle(self, state):
        # send command
        try:
            self.serialObject.write(self.genCmdPacket((self.DISABLE_WATERING_CYCLE_CMD,self.ENABLE_WATERING_CYCLE_CMD)[state]))
        except serial.serialutil.SerialException:
            return False
        return True
