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
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData

class GetSystemPerformanceResourceHandler(ObservableResource, ISystemPerformanceDataListener):
	"""
	Observable resource that will collect system performance data based on the
	given name from the data message listener implementation.
	
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
		self.sysPerfData = None
		
		# for testing
		self.payload = "GetSysPerfData"
		
	def onSystemPerformanceDataUpdate(self, data: SystemPerformanceData) -> bool:
		logging.info("onSystemPerformanceDataUpdate called with data "+SystemPerformanceData)
		
		return aiocoap.message(code = Code.VALID)
	
	async def render_get(self, request):
		responseCode = Code.CONTENT # TODO: change to appropriate value
		
		if not self.sysPerfData:
			self.sysPerfData = SystemPerformanceData()
			
		jsonData = self.dataUtil.systemPerformanceDataToJson(self.sysPerfData)
			
		return aiocoap.Message(code = responseCode, payload = jsonData.encode('ascii'))
	