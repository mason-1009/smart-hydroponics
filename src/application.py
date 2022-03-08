#!/usr/bin/env python3

import cherrypy
import json
import serial
import schedule
import threading
import logging
import argparse

import sys
import os
import time

import camera
import control
import auto

# define global constants
LIGHT_ON=True
LIGHT_OFF=False

WATERING_ON=True
WATERING_OFF=False

AUTO_ENABLED=True
AUTO_DISABLED=False

ENABLED=True
DISABLED=False

class Application(object):

    STATICPATH=None
    serverConfig=dict()

    subsystemSettings=dict()
    
    # settings to disable specific subsystems
    # all subsystems enabled by default
    subsystemSettings["camera"]=ENABLED
    subsystemSettings["controller"]=ENABLED

    # define related objects
    cameraObject=None
    controlObject=None
    automationObject=None
    automationScheduler=None
    automationThread=None

    globalData=dict()

    globalData["soilHumidity"]=None
    globalData["wateringCycleEnabled"]=WATERING_OFF
    globalData["ambientLightStatus"]=LIGHT_OFF
    globalData["warningCodes"]=None
    globalData["growthLampStatus"]=LIGHT_OFF
    globalData["powerDrawData"]=None
    globalData["autocontrolStatus"]=AUTO_ENABLED

    def packWarningCodes(self):
        self.globalData["warningCodes"]=self.subsystemSettings

    def autocontrolThreadedLoop(self):
        # run by monitor engine
        logging.debug("Running pending tasks")
        self.automationScheduler.run_pending()

    def setGrowthLamp(self, state):
        if self.subsystemSettings["controller"]==ENABLED:
            if self.controlObject.setGrowthLamp(state=state):
                logging.info("Growth lamp was configured manually")
                self.globalData["growthLampStatus"]=state
            else:
                logging.error("Attempt to set growth lamp status returned false")
                logging.error("Please try again")

    def setAmbientLighting(self, state):
        if self.subsystemSettings["controller"]==ENABLED:
            if self.controlObject.setAmbientLighting(state=state):
                logging.info("Ambient lighting was configured manually")
                self.globalData["ambientLightStatus"]=state
            else:
                logging.error("Attempt to set ambient light status returned false")
                logging.error("Please try again")

    def setWateringCycle(self, state):
        if self.subsystemSettings["controller"]==ENABLED:
            if self.controlObject.setWateringCycle(state=state):
                logging.info("Watering cycle was configured manually")
                self.globalData["wateringCycleEnabled"]=state
            else:
                logging.error("Attempt to set watering cycle returned false")
                logging.error("Please try again")

    def setAutocontrolStatus(self, state):
        self.globalData["autocontrolStatus"]=state
        if self.globalData["autocontrolStatus"]==ENABLED:
            logging.info("Autocontrol is now enabled")
        elif self.globalData["autocontrolStatus"]==DISABLED:
            logging.info("Autocontrol is now disabled")

    def automation_enableGrowthLamp(self):
        if self.subsystemSettings["controller"]==ENABLED:
            if self.automationObject.automaticGrowthlampEnabled:
                logging.info("Automation system is automatically enabling growth lamp")
                self.globalData["growthLampStatus"]=LIGHT_ON
                self.controlObject.setGrowthLamp(state=LIGHT_ON)
            else:
                logging.info("Automation disabled; growth lamp will not be enabled")
        else:
            logging.info("Automation action cancelled due to dry run setting")
    
    def automation_disableGrowthLamp(self):
        if self.subsystemSettings["controller"]==ENABLED:
            if self.automationObject.automaticGrowthlampEnabled:
                logging.info("Automation system is automatically disabling growth lamp")
                self.globalData["growthLampStatus"]=LIGHT_OFF
                self.controlObject.setGrowthLamp(state=LIGHT_OFF)
            else:
                logging.info("Automation disabled; growth lamp will not be disabled")
        else:
            logging.info("Automation action cancelled due to dry run setting")

    def automation_enableAmbientLighting(self):
        if self.subsystemSettings["controller"]==ENABLED:
            if self.automationObject.automaticAmbientLightingEnabled:
                logging.info("Automation system is automatically enabling ambient lighting")
                self.globalData["ambientLightStatus"]=LIGHT_ON
                self.controlObject.setAmbientLight(state=LIGHT_ON)
            else:
                logging.info("Automation disabled; ambient lighting will not be enabled")
        else:
            logging.info("Automation action cancelled due to dry run setting")

    def automation_disableAmbientLighting(self):
        if self.subsystemSettings["controller"]==ENABLED:
            if self.automationObject.automaticAmbientLightingEnabled:
                logging.info("Automation system is automatically disabling ambient lighting")
                self.globalData["ambientLightStatus"]=LIGHT_OFF
                self.controlObject.setAmbientLight(state=LIGHT_OFF)
            else:
                logging.info("Automation disabled; ambient lighting will not be disabled")
        else:
            logging.info("Automation action cancelled due to dry run setting")

    def automation_startWateringCycle(self):
        if self.subsystemSettings["controller"]==ENABLED:
            if self.automationObject.automaticWateringEnabled:
                logging.info("Automation system is automatically starting watering system")
                self.globalData["wateringCycleEnabled"]=WATERING_ON
                self.controlObject.setWateringCycle(state=WATERING_ON)
            else:
                logging.info("Automation disabled; watering system will not be started")
        else:
            logging.info("Automation action cancelled due to dry run setting")

    def automation_stopWateringCycle(self):
        if self.subsystemSettings["controller"]==ENABLED:
            if self.automationObject.automaticWateringEnabled:
                logging.info("Automation system is automatically stopping watering system")
                self.globalData["wateringCycleEnabled"]=WATERING_OFF
                self.controlObject.setWateringCycle(state=WATERING_OFF)
            else:
                logging.info("Automation disabled; watering system will not be stopped")
        else:
            logging.info("Automation action cancelled due to dry run setting")

    def initiallizeSubsystems(self):
        # initiallize habitat camera
        if self.subsystemSettings["camera"]==ENABLED:
            logging.debug("Initiallizing webcam")
            self.cameraObject=camera.webcam()
            # test for working camera object
            if not self.cameraObject.getCameraFunctionality():
                logging.error("Could not initiallize hab camera - enabling camera dry run")
                self.subsystemSettings["camera"]=DISABLED
        else:
            logging.info("Webcam will not be initiallized due to dry run setting")
        
        # initiallize control subsystem
        if self.subsystemSettings["controller"]==ENABLED:
            logging.debug("Initiallizing controller subsystem")
            # attempt to make contact with serial device
            try:
                self.controlObject=control.Controller()
            except serial.serialutil.SerialException:
                # disable controller subsystem on serial failure
                logging.error("Could not initiallize serial port - enabling serial dry run")
                self.subsystemSettings["controller"]=DISABLED
        else:
            logging.info("Controller will not be initiallized because of dry run setting")

        # disable request logging
        cherrypy.log.access_log.propagate=False
        cherrypy.log.screen=False

        # initiallize threaded autocontrol loop
        logging.debug("Initiallizing threaded autocontrol subsystem")
        self.automationObject=auto.Automation()
        self.automationScheduler=schedule.Scheduler()
        self.automationThread=threading.Thread(target=self.autocontrolThreadedLoop)
        # cherrypy.process.plugins.Monitor(cherrypy.engine, self.autocontrolThreadedLoop, frequency=1).subscribe()
        cherrypy.process.plugins.BackgroundTask(interval=1,function=self.autocontrolThreadedLoop,bus=cherrypy.engine).start()
        
        # configure scheduler
        logging.debug("Setting autocontrol scheduler events")
        self.automationScheduler.every().day.at(self.automationObject.eventTimes["growthlampStart"]).do(self.automation_enableGrowthLamp)
        self.automationScheduler.every().day.at(self.automationObject.eventTimes["growthlampStop"]).do(self.automation_disableGrowthLamp)
        self.automationScheduler.every().day.at(self.automationObject.eventTimes["ambientLightStart"]).do(self.automation_enableAmbientLighting)
        self.automationScheduler.every().day.at(self.automationObject.eventTimes["ambientLightStop"]).do(self.automation_disableAmbientLighting)
        if self.subsystemSettings["controller"]==ENABLED:
            self.automationScheduler.every(3).seconds.do(self.controlObject.fetchInformation)
        else:
            logging.info("Controller information polling will not be enabled due to dry run setting")

        # start autocontrol loop thread
        # self.automationThread.start()

    def __init__(self, disableCamera=False, disableController=False):
        # set static directory handling
        self.STATICPATH=os.path.abspath(os.path.join(os.path.dirname(__file__),"site"))
        self.serverConfig["/"]={"tools.staticdir.on":True,"tools.staticdir.dir":self.STATICPATH,"tools.staticdir.index":"main.html"}

        if disableCamera: logging.info("Disabled camera subsystem")
        if disableController: logging.info("Disabled controller subsystem")

        self.subsystemSettings["camera"]=not disableCamera
        self.subsystemSettings["controller"]=not disableController

        # set up external libraries and hardware objects
        self.initiallizeSubsystems()

    def assembleGlobalJSONPacket(self):
        return json.dumps(self.globalData)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def action(self):
        responseData=cherrypy.request.json

        # define command-specific controller actions
        if responseData.get("mode")==None or responseData.get("mode")=="normal":
            if responseData.get("command")=="set":
                if responseData.get("subsystem")=="growthlamp":
                    if responseData.get("state")!=None:
                        self.setGrowthLamp(state=responseData.get("state"))
                elif responseData.get("subsystem")=="ambientlighting":
                    if responseData.get("state")!=None:
                        self.setAmbientLighting(state=responseData.get("state"))
                elif responseData.get("subsystem")=="watering":
                    if responseData.get("state")!=None:
                        self.setWateringCycle(state=responseData.get("state"))
                elif responseData.get("subsystem")=="autocontrol":
                    if responseData.get("state")!=None:
                        self.setAutocontrolStatus(state=responseData.get("state"))

        # return JSON globaldata regardless of action success
        return self.globalData

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def info(self):
        self.packWarningCodes()
        return self.globalData

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def subsystems(self):
        return self.subsystemSettings

    @cherrypy.expose
    def habview(self):
        # capture new image on request
        if self.subsystemSettings["camera"]==ENABLED:
            self.cameraObject.captureImage()
            cherrypy.response.headers["Content-Type"] = "image/jpg"
            # disable caching for image refreshes
            cherrypy.response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            cherrypy.response.headers["Cache"] = "no-cache"
            cherrypy.response.headers["Expires"] = "0"
            return self.cameraObject.returnJPEGdata()
        else:
            logging.info("Camera has not been initiallized due to dry run setting")
            return None

if __name__ == "__main__":
    # configure application logging
    logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))

    # configure command line arguments
    optionParser=argparse.ArgumentParser()
    #optionParser.add_argument("--dry-run",dest="dryrun",help="Run program without initiallizing physical hardware",default=False,action="store_true")
    optionParser.add_argument("--disable-camera",dest="disableCamera",help="Disable habitat view camera subsystem",default=False,action="store_true")
    optionParser.add_argument("--disable-controller",dest="disableController",help="Disable habitat controller subsystem",default=False,action="store_true")
    optionParser.add_argument("--debug",dest="debug",help="Enable debugging log level",default=False,action="store_true")
    parsedCLIArguments=optionParser.parse_args()

    # create application context and set command line arguments
    appContext = Application(disableCamera=parsedCLIArguments.disableCamera,disableController=parsedCLIArguments.disableController)

    cherrypy.quickstart(appContext,"/",appContext.serverConfig)
