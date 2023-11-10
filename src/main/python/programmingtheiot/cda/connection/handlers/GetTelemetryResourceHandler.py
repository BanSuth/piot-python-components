#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import logging
import aiocoap

from aiocoap import Code
from aiocoap.resource import ObservableResource

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener 
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener

from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SensorData import SensorData

class GetTelemetryResourceHandler(ObservableResource, ITelemetryDataListener):
	"""
	Observable resource that will collect telemetry based on the given
	name from the data message listener implementation.
	
	NOTE: Your implementation will likely need to extend from the selected
	CoAP library's observable resource base class.
	
	"""

	def __init__(self):
		super().__init__()
		
		self.pollCycles = \
			ConfigUtil().getInteger( \
				section = ConfigConst.CONSTRAINED_DEVICE, \
				key = ConfigConst.POLL_CYCLES_KEY, \
				defaultVal = ConfigConst.DEFAULT_POLL_CYCLES)
		
		self.dataUtil = DataUtil()
		self.sensorData = None
		
		# for testing
		self.payload = "GetSensorData"
		
	def onSensorDataUpdate(self, data: SensorData = None) -> bool:
		logging.info("onSensorDataUpdate called with data ")
		responseCode = Code.VALID
		
		return True
	
	async def render_get(self, request):
		responseCode = Code.CONTENT # TODO: change to appropriate value
		
		if not self.sensorData:
			self.sensorData = SensorData()
			
		jsonData = self.dataUtil.sensorDataToJson(self.sensorData)
		logging.info("render_get called with data "+request)
		#return aiocoap.message(code = Code.VALID)	
		return aiocoap.Message(code = responseCode, payload = jsonData.encode('ascii'))
	
	