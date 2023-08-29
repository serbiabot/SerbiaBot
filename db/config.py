from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str('BOT_TOKEN')
ADMINS = env.list("ADMINS")
NOTIFICATIONS_LIMIT = 7200

DB_PATH = '/app/db/database.db'
# DB_PATH = 'database.db'
database_url = f"sqlite:///{DB_PATH}"

engine = create_engine(database_url, echo=True)
Base = declarative_base()
