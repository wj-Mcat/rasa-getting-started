import asyncio
import os
from typing import List

from wechaty import Wechaty, Room, Friendship
from wechaty_plugin_contrib.rasa_rest_plugin import RasaRestPlugin, RasaRestPluginOptions
from wechaty_plugin_contrib import DingDongPlugin
from wechaty_puppet import EventReadyPayload, get_logger

logger = get_logger("BotBay")


class Bot(Wechaty):
    async def on_ready(self, payload: EventReadyPayload):
        rooms: List[Room] = await self.Room.find_all()
        for room in rooms:
            logger.info(room)

    async def on_friendship(self, friendship: Friendship):
        await friendship.accept()


async def run():
    bot = Bot()
    os.environ['token'] = 'e5c6203f-7d77-40f8-8efa-5ca906acdd5c'
    os.environ['endpoint'] = f'http://104.46.232.193:9001'

    rasa_plugin_option = RasaRestPluginOptions(
        endpoint=f'http://104.46.232.193:51103',
        conversation_ids=['21300784018@chatroom', '20923395049@chatroom', 'wxid_gwemn8cbz51621']
    )
    rasa_plugin = RasaRestPlugin(options=rasa_plugin_option)

    ding_dong_plugin = DingDongPlugin()

    bot.use(rasa_plugin).use(ding_dong_plugin)
    await bot.start()


asyncio.run(run())
