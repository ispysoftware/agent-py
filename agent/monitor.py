"""Classes that allow interacting with specific Agent monitors."""

import logging
from enum import Enum
from typing import Optional
from urllib.parse import urlencode

_LOGGER = logging.getLogger(__name__)

class MonitorState(Enum):
	"""Represents the current state of the Monitor."""

	NONE = 'None'
	MONITOR = 'Monitor'
	MODECT = 'Modect'
	RECORD = 'Record'
	REDECT = 'Redect'


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


class Monitor:
	"""Represents a Monitor from Agent."""

	def __init__(self, client, raw_result):
		"""Create a new Monitor."""
		self._client = client
		self._raw_result = raw_result
		self._monitor_id = int(raw_result['id'])
		self._monitor_url = 'command.cgi?cmd=getObject&oid={0}&ot=2'.format(self._monitor_id)
		self._name = raw_result['name']
		self._controllable = True
		self._mjpeg_image_url = 'video.mjpg?oids={0}'.format(self._monitor_id)
		self._still_image_url = 'grab.jpg?oid={0}'.format(self._monitor_id)
		self._mp4_url = 'video.mp4?oid={0}'.format(self._monitor_id)
		self._webm_url = 'video.webm?oid={0}'.format(self._monitor_id)


	@property
	def id(self) -> int:
		"""Get the Agent id number of this Monitor."""
		# pylint: disable=invalid-name
		return self._monitor_id

	@property
	def name(self) -> str:
		"""Get the name of this Monitor."""
		return self._name

	def update_monitor(self):
		"""Update the monitor and monitor status from the Agent server."""
		result = self._client.get_state(self._monitor_url)
		self._raw_result = result
		self._name = result['name']

	@property
	def function(self) -> MonitorState:
		"""Get the MonitorState of this Monitor."""
		self.update_monitor()

		return MonitorState(self._raw_result['function'])

	@function.setter
	def function(self, new_function):
		"""Set the MonitorState of this Monitor."""
		self._client.get_state('command.cgi?cmd=setobjectstate&oid={0}&ot=2&state={1}'.format(self._monitor_id, new_function.value))

	@property
	def controllable(self) -> bool:
		"""Indicate whether this Monitor is movable."""
		return self._controllable

	@property
	def mjpeg_image_url(self) -> str:
		"""Get the motion jpeg (mjpeg) image url of this Monitor."""
		return self._mjpeg_image_url
	
	@property
	def mp4_url(self) -> str:
		"""Get the mp4 video url of this Monitor."""
		return self._mp4_url
	
	@property
	def webm_url(self) -> str:
		"""Get the mp4 video url of this Monitor."""
		return self._webm_url

	@property
	def still_image_url(self) -> str:
		"""Get the still jpeg image url of this Monitor."""
		return self._still_image_url

	@property
	def is_recording(self) -> Optional[bool]:
		"""Indicate if this Monitor is currently recording."""
		status_response = self._client.get_state(self._monitor_url)

		if not status_response:
			_LOGGER.warning('Could not get status for monitor {}'.format(
				self._monitor_id
			))
			return None

		return status_response['data']['recording']

	@property
	def is_available(self) -> bool:
		"""Indicate if this Monitor is currently available."""
		status_response = self._client.get_state(self._monitor_url)

		if not status_response:
			_LOGGER.warning('Could not get availability for monitor {}'.format(
				self._monitor_id
			))
			return False

		return status_response['data']['connected']

	def get_events(self, time_period) -> Optional[int]:
		"""Get the number of events that have occurred on this Monitor.

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
		
		count_response = self._client.get_state(
			'eventcounts.json?oid={0}&ot=2&secs={1}'.format(self._monitor_id, date_filter)
		)
		return count_response['count']
