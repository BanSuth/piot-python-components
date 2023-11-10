#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import logging

from threading import Thread
from time import sleep

import asyncio
import traceback
import threading
import time

from aiocoap.resource import Resource

import aiocoap
import aiocoap.resource as resource



import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.handlers.GetTelemetryResourceHandler import GetTelemetryResourceHandler
from programmingtheiot.cda.connection.handlers.UpdateActuatorResourceHandler import UpdateActuatorResourceHandler
from programmingtheiot.cda.connection.handlers.GetSystemPerformanceResourceHandler import GetSystemPerformanceResourceHandler

class CoapServerAdapter():
	"""
	Definition for a CoAP communications server, with embedded test functions.
	
	"""
	def _initServer(self):
		try:
			# Resource tree creation - lib-specific (this next line of code assumes use of aiocoap)
			self.rootResource = resource.Site()
			
			self.rootResource.add_resource( \
				['.well-known', 'core'], \
				resource.WKCResource(self.rootResource.get_resources_as_linkheader))
			
			self.addResource( \
				resourcePath = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, \
				endName = ConfigConst.HUMIDIFIER_ACTUATOR_NAME, \
				resource = UpdateActuatorResourceHandler(dataMsgListener = self.dataMsgListener))
				
			# TODO: add other actuator resource handlers (for HVAC, etc.)
			
			sysPerfDataListener = GetSystemPerformanceResourceHandler()
			
			self.addResource( \
				resourcePath = ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE, \
				resource = sysPerfDataListener)
			
			# TODO: add other telemetry resource handlers (for SensorData)
			
			# register the callbacks with the data message listener instance
			self.dataMsgListener.setSystemPerformanceDataListener(listener = sysPerfDataListener)
			
			logging.info("Created CoAP server with default resources.")
		except Exception as e:
			traceback.print_exception(type(e), e, e.__traceback__)
			logging.warning("Failed to create CoAP server.")
			
	def __init__(self, dataMsgListener = None):
		self.config = ConfigUtil()
		self.dataMsgListener = dataMsgListener
		self.enableConfirmedMsgs = False
		
		# NOTE: host may need to be the actual IP address - see Kanban board notes
		self.host = self.config.getProperty(ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)
		self.port = self.config.getInteger(ConfigConst.COAP_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_COAP_PORT)
		
		self.coapServer     = None
		self.coapServerTask = None
		
		
		# NOTE: the self.listenTimeout = 30 only used for CoAPthon3
		self.listenTimeout = 30
		
		self.rootResource = None
		
		logging.info("CoAP server configured for host and port: coap://%s:%s", self.host, str(self.port))
		
	def addResource(self, resourcePath: ResourceNameEnum = None, endName: str = None, resource = None):
		if resourcePath and resource:
			uriPath = resourcePath.value
			
			if endName:
				uriPath = uriPath + '/' + endName
				
			resourceList = uriPath.split('/')
			
			if not self.rootResource:
				self.rootResource = aiocoap.resource.Site()
	
			self.rootResource.add_resource(resourceList, resource)
		else:
			logging.warning("No resource provided for path: " + uriPath)
				
	def startServer(self):
		if not self.coapServer:
			logging.info("Starting Async CoAP server...")
			
			try:
				threading.Thread(target = self._runServerTask, daemon = True).start()
				
				logging.info("\n\n***** Async CoAP server STARTED. *****\n\n")
			except Exception as e:
				traceback.print_exception(type(e), e, e.__traceback__)
				logging.warn("Failed to start Async CoAP server.")
		else:
			logging.warn("Async CoAP server not yet initialized (shouldn't happen).")
	
	def stopServer(self):
		if self.coapServer:
			logging.info("Shutting down CoAP server...")
			self._shutdownServerTask()
		
	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		if listener:
			self.dataMsgListener = listener
	def _shutdownServerTask(self):
		asyncio.run(self._shutdownServer())
		
	async def _shutdownServer(self):
		try:
			await self.coapServer.shutdown()
			logging.info("\n\n***** Async CoAP server SHUTDOWN. *****\n\n")
		except Exception as e:
			traceback.print_exception(type(e), e, e.__traceback__)
			logging.warn("Failed to shutdown Async CoAP server.")
	
	def _runServerTask(self):
		asyncio.run(self._runServer())
		
	async def _runServer(self):
		if self.rootResource:
			logging.info('Creating server context...')
	
			bindTuple = (self.host, self.port)
			
			self.coapServer = \
				await aiocoap.Context.create_server_context( \
					site = self.rootResource, \
					bind = bindTuple)
			
			logging.info('Starting running loop - asyncio create_future()...')
			
			await asyncio.get_running_loop().create_future()
		else:
			logging.warning("Root resource not yet created. Can't start server.")
