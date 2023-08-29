from aiogram import executor
from apscheduler.triggers.cron import CronTrigger

from db.config import Base, engine
from handlers.users.search import search_dp as dp
from jobs.jobs import send_advertising_notifications
from loader import scheduler
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)

if __name__ == '__main__':
    scheduler.start()

    import logging
    logging.disable(logging.CRITICAL)

    trigger = CronTrigger(hour=12)
    scheduler.add_job(func=send_advertising_notifications, trigger=trigger)

    Base.metadata.create_all(engine)
    executor.start_polling(dp, skip_updates=True)
