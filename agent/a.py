"""An API Client to interact with Agent."""
import logging
from typing import List, Optional
from urllib.parse import urljoin

import requests

from agent.device import Device
from agent.profile import Profile

_LOGGER = logging.getLogger(__name__)


class Agent:
	"""The Agent API client itself. Create one of these to begin."""

	DEFAULT_SERVER_PATH = '/'
	DEFAULT_TIMEOUT = 10
	OBJECTS_URL = 'command.cgi?cmd=getObjects'

	def __init__(self, server_host) -> None:
		"""Create an Agent API Client."""
		self._server_url = Agent._build_server_url(server_host)
		self._raw_result = self.get_state('command.cgi?cmd=getStatus')

	def get_state(self, api_url)  -> dict:
		"""Perform a GET request on the specified Agent API URL."""
		return self._agent_request('get', api_url)

	def _agent_request(self, method, api_url,timeout=DEFAULT_TIMEOUT) -> dict:
		try:
			req = requests.request(method,urljoin(self._server_url, api_url),timeout=timeout,verify=False)
			if not req.ok:
				_LOGGER.error('Unable to get API response from Agent')			   

			try:
				return req.json()
			except ValueError:
				_LOGGER.exception('JSON decode exception caught while'
								  'attempting to decode "%s"', req.text)
				return None
		except requests.exceptions.ConnectionError:
			_LOGGER.exception('Unable to connect to Agent')
			return None

	def get_devices(self) -> List[Device]:
		"""Get a list of devices from the Agent API."""
		raw_objects = self._agent_request('get', Agent.OBJECTS_URL)
		if not raw_objects:
			_LOGGER.warning("Could not fetch devices from Agent")
			return []

		devices = []
		for raw_result in raw_objects['objectList']:
			_LOGGER.debug("Initializing device %s", raw_result['id'], raw_result['typeID'])
			devices.append(Device(self, raw_result))

		return devices
	
	def get_profiles(self) -> List[Profile]:
		"""Get a list of Profiles from the Agent API."""
		raw_profiles = self.get_state('command.cgi?cmd=getProfiles')
		if not raw_profiles:
			_LOGGER.warning("Could not fetch profiles from Agent")
			return []

		profiles = []
		for raw_profile in raw_profiles['profiles']:
			profiles.append(Profile(self, raw_profile))

		return profiles

	def get_active_profile(self) -> Optional[str]:
		"""Get the name of the active profile from the Agent API."""
		for profile in self.get_profiles():
			if profile.active:
				return profile.name
		return None

	def set_active_profile(self, profile_name):
		"""Set the Agent profile to the given id."""
		_LOGGER.debug('Setting Agent alert profile to %s', profile_name)
		return self.get_state('command.cgi?cmd=setProfileByName&name={0}'.format(profile_name))

	def arm(self):
		"""Arm Agent."""
		self.get_state('command.cgi?cmd=arm')

	def disarm(self):
		"""Disarm Agent."""
		self.get_state('command.cgi?cmd=disarm')

	def update(self):
		self._raw_result = self.get_state('command.cgi?cmd=getStatus')

	@property
	def is_available(self) -> bool:
		"""Indicate if this Agent service is currently available."""
		if not self.raw_result:
			return False
		return True

	@property
	def name(self) -> str:
		"""Return name of the server."""
		return self._raw_result["name"]

	@property
	def unique(self) -> str:
		"""Return unique identifier for the server."""
		return self._raw_result["unique"]

	@property
	def version(self) -> str:
		"""Return version of the server."""
		return self._raw_result["version"]

	@property
	def raw_result(self) -> dict:
		return self._raw_result

	@property
	def is_armed(self) -> bool:
		"""Indicate if Agent is armed."""
		return self._raw_result['armed']

	@staticmethod
	def _build_server_url(server_host) -> str:
		"""Build the server url making sure it ends in a trailing slash."""
		if server_host[-1] == '/':
			return server_host
		return '{}/'.format(server_host)
