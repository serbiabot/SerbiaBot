from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, func, event
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy_utils import ChoiceType

from db import enums, config
from db.config import Base
from db.enums import Language, Rooms, RealEstate, Cities, PropertyCondition
from jobs.jobs import jobs_send_batch
from loader import scheduler


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = Column(
        Integer(),
        primary_key=True,
        autoincrement=True,
    )

    chat_id: Mapped[int] = Column(
        String(),
        nullable=False,
    )

    language: Mapped[str] = Column(
        ChoiceType(Language, impl=String()),
        default=Language.En,
        nullable=False,
    )

    notifications: Mapped[bool] = Column(
        Boolean(),
        default=True,
        nullable=False,
    )

    renew_data: Mapped[bool] = Column(
        Boolean(),
        default=False,
        nullable=False,
    )

    information_availability: Mapped[bool] = Column(
        Boolean(),
        default=True,
        nullable=False,
    )

    last_update = Column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    search_options: Mapped['SearchOption'] = relationship(
        back_populates='user',
    )


class SearchOption(Base):
    __tablename__ = 'search_options'

    id: Mapped[int] = Column(
        Integer(),
        primary_key=True,
        autoincrement=True,
    )

    city: Mapped[str] = Column(
        ChoiceType(Cities, impl=String()),
        nullable=False,
    )

    rooms: Mapped[int] = Column(
        ChoiceType(Rooms, impl=String()),
        nullable=True,
    )

    real_estate_type: Mapped[str] = Column(
        ChoiceType(RealEstate, impl=String()),
        nullable=False,
    )

    condition: Mapped[str] = Column(
        ChoiceType(PropertyCondition, impl=String()),
        nullable=False,
    )

    min_price: Mapped[int] = Column(
        Integer(),
        nullable=False,
        default=0,
    )

    max_price: Mapped[int] = Column(
        Integer(),
        nullable=False,
        default=50000000
    )

    min_price_m2: Mapped[int] = Column(
        Integer(),
        nullable=False,
        default=0,
    )

    max_price_m2: Mapped[int] = Column(
        Integer(),
        nullable=False,
        default=10000
    )

    min_area: Mapped[int] = Column(
        Integer(),
        nullable=True,
    )

    max_area: Mapped[int] = Column(
        Integer(),
        nullable=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
    ) 

    user: Mapped['User'] = relationship(
        back_populates='search_options',
    )


class Advertisement(Base):
    __tablename__ = 'advertisement'

    id: Mapped[int] = Column(
        Integer(),
        primary_key=True,
        autoincrement=True,
    )

    description: Mapped[str] = Column(
        String(),
        nullable=False,
    )

    image: Mapped[str] = Column(
        String(),
        nullable=True
    )


def on_description_change(target, value, oldvalue, initiator):

    if value in [enums.RealEstate.EN_HOUSE, enums.RealEstate.RU_HOUSE]:
        target.rooms = enums.Rooms.HOUSE_1_2
    else:
        target.rooms = enums.Rooms.APART_1_2


def switch_notifications(target, value, oldvalue, initiator):
    try:
        scheduler.remove_job(f'{target.chat_id}_notifications')
    except:
        pass
    if value == True:
        from utils.general import get_user
        scheduler.add_job(
            jobs_send_batch,
            'interval',
            seconds=config.NOTIFICATIONS_LIMIT,
            args=[target.chat_id, get_user(target.chat_id)],
            id=f'{target.chat_id}_notifications'
        )


event.listen(SearchOption.real_estate_type, 'set', on_description_change)
event.listen(User.notifications, 'set', switch_notifications)
