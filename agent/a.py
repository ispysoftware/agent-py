"""An API Client to interact with Agent."""
import logging
from typing import List, Optional
from urllib.parse import urljoin

import requests

from agent.monitor import Monitor
from agent.profile import Profile

_LOGGER = logging.getLogger(__name__)


class Agent:
	"""The Agent API client itself. Create one of these to begin."""

	DEFAULT_SERVER_PATH = '/'
	DEFAULT_TIMEOUT = 10
	MONITOR_URL = 'command.cgi?cmd=getObjects'

	def __init__(self, server_host) -> None:
		"""Create an Agent API Client."""
		self._server_url = Agent._build_server_url(server_host)

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
				return {}
		except requests.exceptions.ConnectionError:
			_LOGGER.exception('Unable to connect to Agent')
			return {}

	def get_monitors(self) -> List[Monitor]:
		"""Get a list of Monitors from the Agent API."""
		raw_monitors = self._agent_request('get', Agent.MONITOR_URL)
		if not raw_monitors:
			_LOGGER.warning("Could not fetch monitors from Agent")
			return []

		monitors = []
		for raw_result in raw_monitors['objectList']:
			if raw_result['typeID'] == 2:
				_LOGGER.debug("Initializing camera %s", raw_result['id'])
				monitors.append(Monitor(self, raw_result))

		return monitors

	def get_profiles(self) -> List[Profile]:
		"""Get a list of Profiles from the Agent API."""
		raw_profiles = self.get_state('command.cgi?cmd=getProfiles')
		if not raw_profiles:
			_LOGGER.warning("Could not fetch profiles from Agent")
			return []

		profiles = []
		for raw_profile in raw_profiles['profiles']:
			_LOGGER.info("Initializing profile %s", raw_profile['id'])
			profiles.append(Profile(self, raw_profile))

		return profiles

	def get_active_profile(self) -> Optional[str]:
		"""Get the name of the active profile from the Agent API."""
		for profile in self.get_profiles():
			if profile.active:
				return profile.name
		return None

	def set_active_profile(self, profile_id):
		"""
		Set the Agent profile to the given id
		"""
		_LOGGER.info('Setting Agent alert profile to %s', profile_id)
		return self.get_state('command.cgi?cmd=setProfile&ind={0}'.format(id))

	@property
	def is_available(self) -> bool:
		"""Indicate if this Agent service is currently available."""
		status_response = self.get_state(
			'command.cgi?cmd=getStatus'
		)

		if not status_response:
			return False

		return status_response.get('version') != 1

	@staticmethod
	def _build_server_url(server_host) -> str:
		"""Build the server url making sure it ends in a trailing slash."""
		if server_host[-1] == '/':
			return server_host
		return '{}/'.format(server_host)
