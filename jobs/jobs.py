from sqlalchemy import Select
from sqlalchemy.orm import sessionmaker

from db.config import engine
from db.database import redis_get, redis_save
from jobs.utils import clean_jobs
from loader import bot


async def jobs_send_batch(chat_id, user):
    json_data = redis_get(chat_id)
    if json_data:
        from parsers.sendler import ParserHub
        json_data = await ParserHub(chat_id).send_batch(user, json_data, count=2)
        redis_save(chat_id, json_data)
    else:
        await clean_jobs(chat_id)


async def jobs_do_parse(parsers):
    for parser in parsers:
        await parser.parse(renew=False)


async def jobs_append_data(chat_id):
    from parsers.sendler import ParserHub
    for page in range(2, 4):
        await ParserHub(chat_id).logic_of_all_parsers(page=page, renew=True)


async def send_advertising_notifications(admin=None):
    from db.models import Advertisement, User

    session = sessionmaker(bind=engine)()
    user_list = session.execute(Select(User.chat_id).where(User.notifications == True)).fetchall()[0] if not admin else [admin]
    advertisement = session.query(Advertisement).first()

    for user_id in user_list:
        if advertisement.image:
            await bot.send_photo(
                chat_id=user_id,
                photo=advertisement.image,
                caption=advertisement.description
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=advertisement.description
            )

    session.close()
