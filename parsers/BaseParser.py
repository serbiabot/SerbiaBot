from db import config
from db.database import redis_save
from jobs.jobs import jobs_send_batch
from loader import scheduler
from parsers.sendler import ParserHub
from utils.general import get_user


class BaseParser:
    def __init__(self, chat_id, page=1):
        self.chat_id = chat_id
        self.user = get_user(chat_id)
        self.is_send = False
        self.page = page

    async def parse(self, silent=False, renew=True):
        notices_json = await self.send_request()
        notices_json = await self.send_first_batch(notices_json)\
            if not silent else notices_json
        await self.save_json(notices_json, renew=renew)
        return self.is_send

    async def send_request(self):
        pass

    async def send_first_batch(self, data):
        if data:
            self.is_send = True
            return await ParserHub(self.chat_id).send_batch(self.user, data)

    async def save_json(self, data, renew=True):
        if not scheduler.get_job(f'{self.chat_id}_notifications'):
            scheduler.add_job(
                jobs_send_batch,
                'interval',
                seconds=config.NOTIFICATIONS_LIMIT,
                args=[self.chat_id, self.user],
                id=f'{self.chat_id}_notifications'
            )
        redis_save(self.chat_id, data, renew=renew)
