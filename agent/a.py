"""An API Client to interact with Agent."""
import logging
from typing import List, Optional
from urllib.parse import urljoin
from .exceptions import AgentConnectionError, AgentError

import aiohttp
import socket
import asyncio
import async_timeout

from agent.device import Device
from datetime import datetime

_LOGGER = logging.getLogger(__name__)


class Agent:
	"""The Agent DVR API client. Create one of these to begin."""

	DEFAULT_SERVER_PATH = '/'
	DEFAULT_TIMEOUT = 10
	OBJECTS_URL = 'command.cgi?cmd=getObjects'

	def __init__(self, server_host, session: aiohttp.client.ClientSession = None) -> None:
		"""Create an Agent API Client."""
		self._server_url = Agent._build_server_url(server_host)
		self._session = session or aiohttp.ClientSession()
		self._close_session = False
		if session is None:
			self._close_session = True
		self._conFailed = False 
		self.disconnected = datetime.now()
		self.reconnect_interval = 10
		self.profiles = []
		self.locations = []
		self.devices = []
		self._raw_result = {}
		return None

	async def close(self) -> None:
		if self._session and self._close_session:
			await self._session.close()

	async def get_state(self, api_url)  -> Optional[dict]:
		"""Perform a GET request on the specified Agent API URL."""
		return await self._agent_request('get', api_url)

	async def _agent_request(self, method, api_url,timeout=DEFAULT_TIMEOUT) -> dict:
		if self._conFailed:
			if (datetime.now()-self.disconnected).total_seconds() < self.reconnect_interval:
				return None
		headers = {
			"User-Agent": f"PythonAgentDVR/",
			"Accept": "application/json, text/plain, */*",
		}

		try:
			async with async_timeout.timeout(timeout):
				response = await self._session.request(
					"GET", urljoin(self._server_url, api_url), json=None, headers=headers,
				)
				response.raise_for_status()
		except asyncio.TimeoutError as exception:
			self.disconnected = datetime.now()
			self._conFailed = True
			
			raise AgentConnectionError(
				"Timeout occurred while connecting to Agent DVR server"
			) from exception
		except (
			aiohttp.ClientError,
			aiohttp.ClientResponseError,
			socket.gaierror,
		) as exception:
			self.disconnected = datetime.now()
			self._conFailed = True
			
			raise AgentConnectionError(
				"Error occurred while communicating with Agent DVR server"
			) from exception

		content_type = response.headers.get("Content-Type", "")
		if "application/json" not in content_type:
			self.disconnected = datetime.now()
			self._conFailed = True

			text = await response.text()
			raise AgentError(
				"Unexpected response from the Agent DVR server",
				{"Content-Type": content_type, "response": text},
			)

		json = await response.json()
		if json.get('error') is not None:
			#error from Agent - Server is still available
			raise AgentError(
				"Error from the Agent DVR server",
				{"Content-Type": content_type, "response": json},
			)
		self._conFailed = False
		return json

	async def get_devices(self) -> List[Device]:
		"""Get a list of devices from the Agent API."""
		raw_objects = await self._agent_request('get', Agent.OBJECTS_URL)
		if raw_objects is not None:
			self.devices = []
			self.locations = raw_objects['locations'];
			for raw_result in raw_objects['objectList']:
				self.devices.append(Device(self, raw_result))
		return self.devices
	
	async def get_profiles(self) -> Optional[dict]:
		"""Get a list of Profiles from the Agent API."""
		raw_profiles = await self.get_state('command.cgi?cmd=getProfiles')
		if raw_profiles is not None:
			self.profiles = raw_profiles['profiles']

		return self.profiles

	async def get_active_profile(self) -> Optional[str]:
		"""Get the name of the active profile from the Agent API."""
		profiles = await self.get_profiles()
		if profiles is None:
			return None

		for profile in profiles:
			if profile['active']:
				return profile['name']
		return None

	async def set_active_profile(self, profile_name):
		"""Set the Agent profile to the given id."""
		await self.get_state('command.cgi?cmd=setProfileByName&name={0}'.format(profile_name))

	async def arm(self):
		"""Arm Agent."""
		await self.get_state('command.cgi?cmd=arm')

	async def disarm(self):
		"""Disarm Agent."""
		await self.get_state('command.cgi?cmd=disarm')

	async def update(self):
		state = await self.get_state('command.cgi?cmd=getStatus')
		if state is not None:
			self._raw_result = state

	@property
	def is_available(self) -> bool:
		"""Indicate if this Agent service is currently available."""
		return not self._conFailed

	@property
	def name(self) -> str:
		"""Return name of the server."""
		return self._raw_result["name"]

	@property
	def unique(self) -> str:
		"""Return unique identifier for the server."""
		return self._raw_result["unique"]

	@property
	def remote_access(self) -> bool:
		"""Return unique identifier for the server."""
		return self._raw_result["remoteAccess"]

	@property
	def version(self) -> str:
		"""Return version of the server."""
		return self._raw_result["version"]

	@property
	def raw_result(self) -> dict:
		return self._raw_result

	@property 
	def device_count(self) -> int:
		return self._raw_result["devices"]

	@property
	def is_armed(self) -> bool:
		"""Indicate if Agent is armed."""
		return self._raw_result["armed"]

	@staticmethod
	def _build_server_url(server_host) -> str:
		"""Build the server url making sure it ends in a trailing slash."""
		if server_host[-1] == '/':
			return server_host
		return '{}/'.format(server_host)
