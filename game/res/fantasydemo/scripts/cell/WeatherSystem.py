"This module implements the WeatherSystem entity."

import BigWorld

class WeatherSystem( BigWorld.Entity ):
	"A weather system entity."
	
	def kill( self, names ):
		if len(names) == 0 or self.name in names:
			self.destroy()

def rain( propensity, spaceID = 1, position = (0,0,0) ):
	dict = {}
	dict["name"] = "RAIN"
	dict["propensity"] = propensity
	dict["arg0"] = 1.0
	dict["arg1"] = 1.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def clear( propensity, spaceID = 1, position = (0,0,0) ):
	dict = {}
	dict["name"] = "CLEAR"
	dict["propensity"] = propensity
	dict["arg0"] = 1.0
	dict["arg1"] = 1.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def storm( propensity, spaceID = 1, position = (0,0,0) ):
	dict = {}
	dict["name"] = "STORM"
	dict["propensity"] = propensity
	dict["arg0"] = 1.0
	dict["arg1"] = 1.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def cloud( propensity, spaceID = 1, position = (0,0,0) ):
	dict = {}
	dict["name"] = "CLOUD"
	dict["propensity"] = propensity
	dict["arg0"] = 1.0
	dict["arg1"] = 1.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def temperature( value, spaceID = 1, position = (0,0,0) ):
	dict = {}
	dict["name"] = "TEMPERATURE"
	dict["propensity"] = 0
	dict["arg0"] = value
	dict["arg1"] = 0.0
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def wind( x, y, gustiness, spaceID = 1, position = (0,0,0) ):
	dict = {}
	dict["name"] = "WIND"
	dict["propensity"] = 0
	dict["arg0"] = x
	dict["arg1"] = y
	dict["arg2"] = gustiness
	BigWorld.createEntity( "WeatherSystem", spaceID, position, (0,0,0), dict )

def kill(name = ""):
	for e in BigWorld.entities.values():
		if e.__class__ == WeatherSystem:
			if name == "" or e.name == name:
				e.destroy()

# WeatherSystem.py
