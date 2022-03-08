#!/usr/bin/env python3

class Automation(object):
    
    # define settings
    automaticWateringEnabled=None
    automaticGrowthlampEnabled=None
    automaticAmbientLightingEnabled=None

    # define default times
    eventTimes = dict()

    def __init__(self, automateWatering=False, automateGrowthlamp=False, automateAmbience=False):

        self.eventTimes["growthlampStart"] = "19:50"
        self.eventTimes["growthlampStop"] = "04:00"

        self.eventTimes["ambientLightStart"] = "07:40"
        self.eventTimes["ambientLightStop"] = "02:35"

        self.automaticWateringEnabled=automateWatering
        self.automaticGrowthlampEnabled=automateGrowthlamp
        self.automaticAmbientLightingEnabled=automateAmbience

    def disableAllAutomation(self):
        self.automaticWateringEnabled=False
        self.automaticGrowthlampEnabled=False
        self.automaticAmbientLightingEnabled=False

    def enableAllAutomation(self):
        self.automaticWateringEnabled=True
        self.automaticGrowthlampEnabled=True
        self.automaticAmbientLightingEnabled=True
