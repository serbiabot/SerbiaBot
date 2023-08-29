import datetime

from db.database import redis_clean
from loader import scheduler


async def clean_jobs(chat_id):
    redis_clean(chat_id)
    all_jobs = scheduler.get_jobs()

    for job in all_jobs:
        if str(job.id).startswith(str(chat_id)):
            scheduler.remove_job(job.id)


async def append_parsers_data(user):
    if not scheduler.get_job(f'{user.chat_id}_append_data'):
        from jobs.jobs import jobs_append_data
        scheduler.add_job(
            jobs_append_data,
            'date',
            run_date=datetime.datetime.now() + datetime.timedelta(minutes=30),
            args=[user.chat_id],
            id=f'{user.chat_id}_append_data'
        )
