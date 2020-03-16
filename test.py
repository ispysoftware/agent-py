import unittest
import aiohttp

from agent import a
from agent.device import TimePeriod


import asyncio

async def Test (url):
	tc = a.Agent(url)
	sess = aiohttp.ClientSession()
	tc2 = a.Agent(url,sess)

	await tc.update()
	print(tc.is_available)
	print(await tc.get_profiles())
	print(await tc.get_active_profile())
	print(tc.is_armed)
	print(tc.unique)
	await tc.arm()
	await tc.disarm()
	print(tc.name)
	print(tc.version)
	print(tc.raw_result)
	print(tc.remote_access)
	print(tc.device_count)

	m= await tc.get_devices()
	for o in m:
		print(o.name)
		print(o._client._server_url)
		print(o.id)
		print(o.typeID)
		print(o.mjpeg_image_url)
		print(o.still_image_url)
		print(o.mp4_url)
		print(o.webm_url)
		print(o.recording)
		print(o.alerted)
		print(o.online)
		print(o.detector_active)
		print(o.alerts_active)
		print(o.connected)
		print(o.has_ptz)
		print(o.raw_result)
		await o.snapshot()
		await o.alerts_on()
		await o.alerts_off()
		print(await o.get_events(TimePeriod.HOUR))
		await o.update()

	print(await tc.get_profiles())
	await tc.set_active_profile('home')
	print(await tc.get_active_profile())
	await tc.set_active_profile('away')
	print(await tc.get_active_profile())

	await tc.close()
	await tc2.close()
	await sess.close()

	print("end")

loop = asyncio.get_event_loop()
loop.run_until_complete(Test("http://localhost:8090/"))
