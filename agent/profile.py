"""Classes that allow interacting with Agent Profiles."""

import asyncio
class Profile:
	"""Represents a Profile from Agent."""

	def __init__(self, client, raw_profile):
		"""Create a new Profile."""
		self._client = client
		self._profile_id = int(raw_profile['id'])
		self._profile_url = 'command.cgi?cmd=getProfiles'
		self._name = raw_profile['name']

	@property
	def id(self) -> int:
		"""Get the Agent id number of this Profile."""
		# pylint: disable=invalid-name
		return self._profile_id

	@property
	def name(self) -> str:
		"""Get the name of this Profile."""
		return self._name

	@property
	async def active(self) -> bool:
		"""Indicate if this Profile is currently active."""
		profiles = await self._client.get_state(self._profile_url)['profiles']
		for profile in profiles:
			if int(profile['id']) == self._profile_id:
				return profile['active']
		return False

	async def activate(self):
		"""Activate this Profile."""
		await self._client.set_active_profile(self._profile_id)
