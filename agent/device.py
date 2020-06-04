"""Classes that allow interacting with specific Agent devices."""

import logging
from enum import Enum
from typing import Optional
import asyncio
from urllib.parse import urlencode

_LOGGER = logging.getLogger(__name__)

class TimePeriod(Enum):
	"""Represents a period of time to check for events."""

	@property
	def period(self) -> str:
		"""Get the period of time."""
		# pylint: disable=unsubscriptable-object
		return self.value[0]

	@property
	def title(self) -> str:
		"""Explains what is measured in this period."""
		# pylint: disable=unsubscriptable-object
		return self.value[1]

	@staticmethod
	def get_time_period(value):
		"""Get the corresponding TimePeriod from the value.

		Example values: 'all', 'hour', 'day', 'week', or 'month'.
		"""
		for time_period in TimePeriod:
			if time_period.period == value:
				return time_period
		raise ValueError('{} is not a valid TimePeriod'.format(value))

	ALL = ('all', 'Events')
	HOUR = ('hour', 'Events Last Hour')
	DAY = ('day', 'Events Last Day')
	WEEK = ('week', 'Events Last Week')
	MONTH = ('month', 'Events Last Month')

class Device:
	"""Represents a device from Agent."""

	def __init__(self, client, raw_result):
		"""Create a new device."""
		self._client = client
		self._raw_result = raw_result
		self._oid = int(raw_result['id'])
		self._ot = int(raw_result['typeID'])

	@property
	def id(self) -> int:
		"""Get the Agent id number of this device."""
		# pylint: disable=invalid-name
		return self._oid

	@property
	def typeID(self) -> int:
		"""Get the Agent id number of this device."""
		# pylint: disable=invalid-name
		return self._ot

	@property
	def client(self):
		"""Get the Agent server client of this device."""
		# pylint: disable=invalid-name
		return self._client

	@property
	def name(self) -> str:
		"""Get the name of this device."""
		return self._raw_result['name']


	async def update(self):
		"""Update the device from the Agent server."""
		state = await self._client.get_state('command.cgi?cmd=getObject&oid={0}&ot={1}'.format(self._oid,self._ot))
		if state is not None:
			self._raw_result = state

	@property
	def mjpeg_image_url(self) -> str:
		"""Get the mjpeg url of this device."""
		return 'video.mjpg?oid={0}'.format(self._oid)
	
	@property
	def mp4_url(self) -> str:
		"""Get the mp4 video url of this device."""
		return 'video.mp4?oid={0}'.format(self._oid)
	
	@property
	def webm_url(self) -> str:
		"""Get the mp4 video url of this device."""
		return 'video.webm?oid={0}'.format(self._oid)

	@property
	def still_image_url(self) -> str:
		"""Get the still jpeg image url of this device."""
		return 'grab.jpg?oid={0}'.format(self._oid)

	@property
	def recording(self) -> bool:
		"""Indicate if this device is currently recording."""
		return self._raw_result['data']['recording']
	
	@property
	def alerted(self) -> bool:
		"""Indicate if this device has alerted."""
		return self._raw_result['data']['alerted']
	
	@property
	def detected(self) -> bool:
		"""Indicate if this device has detected."""
		return self._raw_result['data']['detected']

	@property
	def online(self) -> bool:
		"""Indicate if this device is currently online."""
		return self._raw_result['data']['online']

	@property
	def alerts_active(self) -> bool:
		"""Indicate if this device has alerts enabled."""
		return self._raw_result['data']['alertsActive']
	
	@property
	def detector_active(self) -> bool:
		"""Indicate if this device has alerts enabled."""
		return self._raw_result['data']['detectorActive']

	@property
	def connected(self) -> bool:
		"""Indicate if this device is currently connected."""
		return self._raw_result['data']['connected']

	@property
	def has_ptz(self) -> bool:
		"""Indicate if this device has PTZ capability."""
		return self._ot == 2 and self._raw_result['data']['ptzid'] != -1

	@property
	def width(self) -> int:
		"""Get the width of the device."""
		return self._raw_result['data']['width']

	@property
	def height(self) -> int:
		"""Get the height of the device."""
		return self._raw_result['data']['height']
		
	@property
	def mjpegStreamWidth(self) -> int:
		"""Get the computed stream width of the device."""
		if 'mjpegStreamWidth' in self._raw_result['data']:
			return self._raw_result['data']['mjpegStreamWidth']
		return 640

	@property
	def mjpegStreamHeight(self) -> int:
		"""Get the computed stream height of the device."""
		if 'mjpegStreamHeight' in self._raw_result['data']:
			return self._raw_result['data']['mjpegStreamHeight']
		return 480
		
	@property
	def location(self) -> str:
		"""Get the location of the device."""
		ind = self._raw_result['locationIndex']
		if ind > -1 and ind < len(self._client.locations):
			return self._client.locations[ind]['name']
		return ""
	
	@property
	def raw_result(self) -> dict:
		return self._raw_result


	async def enable(self):
		state = await self._client.get_state('command.cgi?cmd=switchOn&oid={0}&ot={1}'.format(self._oid, self._ot))
		if state is not None:
			self._raw_result['data']['online'] = True


	async def disable(self):
		state = await self._client.get_state('command.cgi?cmd=switchOff&oid={0}&ot={1}'.format(self._oid, self._ot))
		if state is not None:
			self._raw_result['data']['online'] = False


	async def record(self):
		state = await self._client.get_state('command.cgi?cmd=record&oid={0}&ot={1}'.format(self._oid, self._ot))
		if state is not None:
			self._raw_result['data']['recording'] = True


	async def record_stop(self):
		state = await self._client.get_state('command.cgi?cmd=recordStop&oid={0}&ot={1}'.format(self._oid, self._ot))
		if state is not None:
			self._raw_result['data']['recording'] = False


	async def alerts_on(self):
		state = await self._client.get_state('command.cgi?cmd=alertOn&oid={0}&ot={1}'.format(self._oid, self._ot))
		if state is not None:
			self._raw_result['data']['alertsActive'] = True


	async def alerts_off(self):
		state = await self._client.get_state('command.cgi?cmd=alertOff&oid={0}&ot={1}'.format(self._oid, self._ot))
		if state is not None:
			self._raw_result['data']['alertsActive'] = False

	async def detector_on(self):
		state = await self._client.get_state('command.cgi?cmd=detectorOn&oid={0}&ot={1}'.format(self._oid, self._ot))
		if state is not None:
			self._raw_result['data']['detectorActive'] = True


	async def detector_off(self):
		state = await self._client.get_state('command.cgi?cmd=detectorOff&oid={0}&ot={1}'.format(self._oid, self._ot))
		if state is not None:
			self._raw_result['data']['detectorActive'] = False

	async def snapshot(self):
		await self._client.get_state('command.cgi?cmd=snapshot&oid={0}&ot={1}'.format(self._oid, self._ot))


	async def get_events(self, time_period) -> Optional[int]:
		"""Get the number of events that have occurred on this device.

		Specifically only gets events that have occurred within the TimePeriod
		provided.
		"""
		date_filter = 3600*24*365*20
		if time_period == TimePeriod.HOUR:
			date_filter = 3600
		
		if time_period == TimePeriod.DAY:
			date_filter = 3600*24
		
		if time_period == TimePeriod.WEEK:
			date_filter = 3600*24*7
		
		if time_period == TimePeriod.MONTH:
			date_filter = 3600*24*30
		
		count_response = await self._client.get_state(
			'eventcounts.json?oid={0}&ot={1}&secs={2}'.format(self._oid, self._ot, date_filter)
		)
		if count_response is None:
			return 0

		return count_response['count']
